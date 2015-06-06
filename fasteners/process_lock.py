# -*- coding: utf-8 -*-

# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import errno
import functools
import itertools
import logging
import os
import threading
import time

import six

from fasteners import _utils

LOG = logging.getLogger(__name__)


def _noop_delay(attempts):
    return None


def _ensure_tree(path):
    """Create a directory (and any ancestor directories required).

    :param path: Directory to create
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            if not os.path.isdir(path):
                raise
            else:
                return False
        else:
            raise
    else:
        return True


class _InterProcessLock(object):
    """An interprocess locking implementation.

    This is a lock implementation which allows multiple locks, working around
    issues like http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=632857 and
    does not require any cleanup. Since the lock is always held on a file
    descriptor rather than outside of the process, the lock gets dropped
    automatically if the process crashes, even if ``__exit__`` is not
    executed.

    There are no guarantees regarding usage by multiple threads in a
    single process here. This lock works only between processes.

    Note these locks are released when the descriptor is closed, so it's not
    safe to close the file descriptor while another thread holds the
    lock. Just opening and closing the lock file can break synchronization,
    so lock files must be accessed only using this abstraction.
    """

    MAX_DELAY = 0.1
    """
    Default maximum delay we will wait to try to acquire the lock (when
    it's busy/being held by another process).
    """

    DELAY_INCREMENT = 0.01
    """
    Default increment we will use (up to max delay) after each attempt before
    next attempt to acquire the lock. For example if 3 attempts have been made
    the calling thread will sleep (0.01 * 3) before the next attempt to
    acquire the lock (and repeat).
    """

    def __init__(self, path, sleep_func=time.sleep):
        self.lockfile = None
        self.path = path
        self.acquired = False
        self.sleep_func = sleep_func

    def _do_acquire(self, delay_func, blocking, watch):
        attempts_iter = itertools.count(1)
        while True:
            attempts = six.next(attempts_iter)
            try:
                self.trylock()
            except IOError as e:
                if e.errno in (errno.EACCES, errno.EAGAIN):
                    if not blocking or watch.expired():
                        return (False, attempts)
                    else:
                        delay_func(attempts)
                else:
                    raise threading.ThreadError("Unable to acquire lock on"
                                                " `%(path)s` due to"
                                                " %(exception)s" %
                                                {
                                                    'path': self.path,
                                                    'exception': e,
                                                })
            else:
                return (True, attempts)

    def _do_open(self):
        basedir = os.path.dirname(self.path)
        made_basedir = _ensure_tree(basedir)
        if made_basedir:
            LOG.info('Created lock base path `%s`', basedir)
        # Open in append mode so we don't overwrite any potential contents of
        # the target file. This eliminates the possibility of an attacker
        # creating a symlink to an important file in our lock path.
        if self.lockfile is None or self.lockfile.closed:
            self.lockfile = open(self.path, 'a')

    def _backoff_multiplier_delay(self, attempts, delay, max_delay):
        maybe_delay = attempts * delay
        if maybe_delay < max_delay:
            actual_delay = maybe_delay
        else:
            actual_delay = max_delay
        actual_delay = max(0.0, actual_delay)
        self.sleep_func(actual_delay)

    def acquire(self, blocking=True,
                delay=DELAY_INCREMENT, max_delay=MAX_DELAY,
                timeout=None):
        if delay < 0:
            raise ValueError("Delay must be greater than or equal to zero")
        if timeout is not None and timeout < 0:
            raise ValueError("Timeout must be greater than or equal to zero")
        if delay >= max_delay:
            max_delay = delay
        self._do_open()
        watch = _utils.StopWatch(duration=timeout)
        if blocking:
            delay_func = functools.partial(self._backoff_multiplier_delay,
                                           delay=delay, max_delay=max_delay)
        else:
            delay_func = _noop_delay
        with watch:
            gotten, attempts = self._do_acquire(delay_func, blocking, watch)
        if not gotten:
            self.acquired = False
            return False
        else:
            self.acquired = True
            LOG.debug("Acquired file lock `%s` after waiting %0.3fs [%s"
                      " attempts were required]", self.path, watch.elapsed(),
                      attempts)
            return True

    def _do_close(self):
        if self.lockfile is not None:
            self.lockfile.close()
            self.lockfile = None

    def __enter__(self):
        self.acquire()
        return self

    def release(self):
        if not self.acquired:
            raise threading.ThreadError("Unable to release an unacquired"
                                        " lock")
        try:
            self.unlock()
        except IOError:
            LOG.exception("Could not unlock the acquired lock opened"
                          " on `%s`", self.path)
        else:
            self.acquired = False
            try:
                self._do_close()
            except IOError:
                LOG.exception("Could not close the file handle"
                              " opened on `%s`", self.path)
            else:
                LOG.debug("Unlocked and closed file lock open on"
                          " `%s`", self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def exists(self):
        return os.path.exists(self.path)

    def trylock(self):
        raise NotImplementedError()

    def unlock(self):
        raise NotImplementedError()


class _WindowsLock(_InterProcessLock):

    def trylock(self):
        msvcrt.locking(self.lockfile.fileno(), msvcrt.LK_NBLCK, 1)

    def unlock(self):
        msvcrt.locking(self.lockfile.fileno(), msvcrt.LK_UNLCK, 1)


class _FcntlLock(_InterProcessLock):

    def trylock(self):
        fcntl.lockf(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def unlock(self):
        fcntl.lockf(self.lockfile, fcntl.LOCK_UN)


if os.name == 'nt':
    import msvcrt

    #: Interprocess lock implementation that works on your system.
    InterProcessLock = _WindowsLock
else:
    import fcntl

    #: Interprocess lock implementation that works on your system.
    InterProcessLock = _FcntlLock


def interprocess_locked(path):
    """Acquires & releases a interprocess lock around call into
       decorated function."""

    lock = InterProcessLock(path)

    def decorator(f):

        @six.wraps(f)
        def wrapper(*args, **kwargs):
            with lock:
                return f(*args, **kwargs)

        return wrapper

    return decorator
