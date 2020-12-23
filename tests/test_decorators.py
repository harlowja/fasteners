# -*- coding: utf-8 -*-

#    Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
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

import threading

import fasteners


class Locked(object):
    def __init__(self):
        self._lock = threading.Lock()

    @fasteners.locked
    def assert_i_am_locked(self):
        assert self._lock.locked()

    def assert_i_am_not_locked(self):
        assert not self._lock.locked()


class ManyLocks(object):
    def __init__(self, amount):
        self._lock = []
        for _i in range(0, amount):
            self._lock.append(threading.Lock())

    @fasteners.locked
    def assert_i_am_locked(self):
        assert all(lock.locked() for lock in self._lock)

    def assert_i_am_not_locked(self):
        assert not any(lock.locked() for lock in self._lock)


class RWLocked(object):
    def __init__(self):
        self._lock = fasteners.ReaderWriterLock()

    @fasteners.read_locked
    def assert_i_am_read_locked(self):
        assert self._lock.owner == fasteners.ReaderWriterLock.READER

    @fasteners.write_locked
    def assert_i_am_write_locked(self):
        assert self._lock.owner == fasteners.ReaderWriterLock.WRITER

    def assert_i_am_not_locked(self):
        assert self._lock.owner is None


def test_locked():
    obj = Locked()
    obj.assert_i_am_locked()
    obj.assert_i_am_not_locked()


def test_many_locked():
    obj = ManyLocks(10)
    obj.assert_i_am_locked()
    obj.assert_i_am_not_locked()


def test_read_write_locked():
    obj = RWLocked()
    obj.assert_i_am_write_locked()
    obj.assert_i_am_read_locked()
    obj.assert_i_am_not_locked()
