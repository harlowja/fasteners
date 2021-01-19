# -*- coding: utf-8 -*-

# Copyright 2011 OpenStack Foundation.
# Copyright 2011 Justin Santa Barbara
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

import contextlib
import errno
import multiprocessing
import os
import shutil
import sys
import tempfile
import threading
import time

import pytest

from fasteners import process_lock as pl

WIN32 = os.name == 'nt'


@contextlib.contextmanager
def scoped_child_processes(children, timeout=0.1, exitcode=0):
    for child in children:
        child.daemon = True
        child.start()
    yield
    start = time.time()
    timed_out = 0

    for child in children:
        child.join(max(timeout - (time.time() - start), 0))
        if child.is_alive():
            timed_out += 1
        child.terminate()

    if timed_out:
        msg = "{} child processes killed due to timeout\n".format(timed_out)
        sys.stderr.write(msg)

    if exitcode is not None:
        for child in children:
            c_code = child.exitcode
            msg = "Child exitcode {} != {}"
            assert c_code == exitcode, msg.format(c_code, exitcode)


def try_lock(lock_file):
    try:
        my_lock = pl.InterProcessLock(lock_file)
        my_lock.lockfile = open(lock_file, 'w')
        my_lock.trylock()
        my_lock.unlock()
        sys.exit(1)
    except IOError:
        sys.exit(0)


def inter_processlock_helper(lockname, lock_filename, pipe):
    lock2 = pl.InterProcessLock(lockname)
    lock2.lockfile = open(lock_filename, 'w')
    have_lock = False
    while not have_lock:
        try:
            lock2.trylock()
            have_lock = True
        except IOError:
            pass
    # Hold the lock and wait for the parent
    pipe.send(None)
    pipe.recv()


@pytest.fixture()
def lock_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture()
def handles_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_lock_acquire_release_file_lock(lock_dir):
    lock_file = os.path.join(lock_dir, 'lock')
    lock = pl.InterProcessLock(lock_file)

    def attempt_acquire(count):
        children = [
            multiprocessing.Process(target=try_lock, args=(lock_file,))
            for i in range(count)]
        with scoped_child_processes(children, timeout=10, exitcode=None):
            pass
        return sum(c.exitcode for c in children)

    assert lock.acquire()
    try:
        acquired_children = attempt_acquire(10)
        assert acquired_children == 0
    finally:
        lock.release()

    acquired_children = attempt_acquire(5)
    assert acquired_children != 0


def test_nested_synchronized_external_works(lock_dir):
    sentinel = object()

    @pl.interprocess_locked(os.path.join(lock_dir, 'test-lock-1'))
    def outer_lock():
        @pl.interprocess_locked(os.path.join(lock_dir, 'test-lock-2'))
        def inner_lock():
            return sentinel

        return inner_lock()

    assert outer_lock() == sentinel


def _lock_files(lock_path, handles_dir, num_handles=50):
    with pl.InterProcessLock(lock_path):

        # Open some files we can use for locking
        handles = []
        for n in range(num_handles):
            path = os.path.join(handles_dir, ('file-%s' % n))
            handles.append(open(path, 'w'))

        # Loop over all the handles and try locking the file
        # without blocking, keep a count of how many files we
        # were able to lock and then unlock. If the lock fails
        # we get an IOError and bail out with bad exit code
        count = 0
        for handle in handles:
            try:
                pl.InterProcessLock._trylock(handle)
                count += 1
                pl.InterProcessLock._unlock(handle)
            except IOError:
                sys.exit(2)
            finally:
                handle.close()

        # Check if we were able to open all files
        if count != num_handles:
            raise AssertionError("Unable to open all handles")


def _do_test_lock_externally(lock_dir_, handles_dir_):
    lock_path = os.path.join(lock_dir_, "lock")

    num_handles = 50
    num_processes = 50
    args = (lock_path, handles_dir_, num_handles)
    children = [multiprocessing.Process(target=_lock_files, args=args)
                for _ in range(num_processes)]

    with scoped_child_processes(children, timeout=30, exitcode=0):
        pass


def test_lock_externally(lock_dir, handles_dir):
    _do_test_lock_externally(lock_dir, handles_dir)


def test_lock_externally_lock_dir_not_exist(lock_dir, handles_dir):
    os.rmdir(lock_dir)
    _do_test_lock_externally(lock_dir, handles_dir)


def test_lock_file_exists(lock_dir):
    lock_file = os.path.join(lock_dir, 'lock')

    @pl.interprocess_locked(lock_file)
    def foo():
        assert os.path.exists(lock_file)

    foo()


def test_bad_release(lock_dir):
    lock_file = os.path.join(lock_dir, 'lock')
    lock = pl.InterProcessLock(lock_file)
    with pytest.raises(threading.ThreadError):
        lock.release()


def test_interprocess_lock(lock_dir):
    lock_file = os.path.join(lock_dir, 'lock')
    lock_name = 'foo'

    child_pipe, them = multiprocessing.Pipe()
    child = multiprocessing.Process(
        target=inter_processlock_helper, args=(lock_name, lock_file, them))

    with scoped_child_processes((child,)):

        # Make sure the child grabs the lock first
        if not child_pipe.poll(5):
            pytest.fail('Timed out waiting for child to grab lock')

        start = time.time()
        lock1 = pl.InterProcessLock(lock_name)
        lock1.lockfile = open(lock_file, 'w')
        # NOTE(bnemec): There is a brief window between when the lock file
        # is created and when it actually becomes locked.  If we happen to
        # context switch in that window we may succeed in locking the
        # file. Keep retrying until we either get the expected exception
        # or timeout waiting.
        while time.time() - start < 5:
            try:
                lock1.trylock()
                lock1.unlock()
                time.sleep(0)
            except IOError:
                # This is what we expect to happen
                break
        else:
            pytest.fail('Never caught expected lock exception')

        child_pipe.send(None)


@pytest.mark.skipif(WIN32, reason='Windows cannot open file handles twice')
def test_non_destructive(lock_dir):
    lock_file = os.path.join(lock_dir, 'not-destroyed')
    with open(lock_file, 'w') as f:
        f.write('test')
    with pl.InterProcessLock(lock_file):
        with open(lock_file) as f:
            assert f.read() == 'test'


class BrokenLock(pl.InterProcessLock):
    def __init__(self, name, errno_code):
        super(BrokenLock, self).__init__(name)
        self.errno_code = errno_code

    def unlock(self):
        pass

    def trylock(self):
        err = IOError()
        err.errno = self.errno_code
        raise err


def test_bad_acquire(lock_dir):
    lock_file = os.path.join(lock_dir, 'lock')
    lock = BrokenLock(lock_file, errno.EBUSY)
    with pytest.raises(threading.ThreadError):
        lock.acquire()


def test_lock_twice(lock_dir):
    lock_file = os.path.join(lock_dir, 'lock')
    lock = pl.InterProcessLock(lock_file)

    ok = lock.acquire(blocking=False)
    assert ok

    # ok on Unix, not ok on Windows
    ok = lock.acquire(blocking=False)
    assert ok or not ok

    # should release without crashing
    lock.release()
