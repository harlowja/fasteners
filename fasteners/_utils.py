# -*- coding: utf-8 -*-

# Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
#
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

import logging

from monotonic import monotonic as now  # noqa

# log level for low-level debugging
BLATHER = 5

LOG = logging.getLogger(__name__)


class LockStack(object):
    """Simple lock stack to get and release many locks.

    An instance of this should **not** be used by many threads at the
    same time, as the stack that is maintained will be corrupted and
    invalid if that is attempted.
    """

    def __init__(self):
        self._stack = []

    def acquire_lock(self, lock):
        gotten = lock.acquire()
        if gotten:
            self._stack.append(lock)
        return gotten

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        am_left = len(self._stack)
        tot_am = am_left
        while self._stack:
            lock = self._stack.pop()
            try:
                lock.release()
            except Exception:
                LOG.exception("Failed releasing lock %s from lock"
                              " stack with %s locks", am_left, tot_am)
            am_left -= 1


class StopWatch(object):
    """A really basic stop watch."""

    def __init__(self, duration=None):
        self.duration = duration
        self.started_at = None
        self.stopped_at = None

    def elapsed(self):
        if self.stopped_at is not None:
            t = self.stopped_at
        else:
            t = now()
        e = t - self.started_at
        return max(0.0, e)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stopped_at = now()

    def start(self):
        self.started_at = now()
        self.stopped_at = None

    def expired(self):
        if self.duration is None:
            return False
        else:
            e = self.elapsed()
            if e > self.duration:
                return True
            return False
