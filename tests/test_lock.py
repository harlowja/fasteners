# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
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

import collections
from concurrent import futures
import random
import threading
import time

import pytest

import fasteners
from fasteners import _utils

# NOTE(harlowja): Sleep a little so now() can not be the same (which will
# cause false positives when our overlap detection code runs). If there are
# real overlaps then they will still exist.
NAPPY_TIME = 0.05

# We will spend this amount of time doing some "fake" work.
WORK_TIMES = [(0.01 + x / 100.0) for x in range(0, 5)]

# If latches/events take longer than this to become empty/set, something is
# usually wrong and should be debugged instead of deadlocking...
WAIT_TIMEOUT = 300

THREAD_COUNT = 20


def _find_overlaps(times, start, end):
    overlaps = 0
    for (s, e) in times:
        if s >= start and e <= end:
            overlaps += 1
    return overlaps


def _spawn_variation(readers, writers, max_workers=None):
    start_stops = collections.deque()
    lock = fasteners.ReaderWriterLock()

    def read_func(ident):
        with lock.read_lock():
            enter_time = time.monotonic()
            time.sleep(WORK_TIMES[ident % len(WORK_TIMES)])
            exit_time = time.monotonic()
            start_stops.append((lock.READER, enter_time, exit_time))
            time.sleep(NAPPY_TIME)

    def write_func(ident):
        with lock.write_lock():
            enter_time = time.monotonic()
            time.sleep(WORK_TIMES[ident % len(WORK_TIMES)])
            exit_time = time.monotonic()
            start_stops.append((lock.WRITER, enter_time, exit_time))
            time.sleep(NAPPY_TIME)

    if max_workers is None:
        max_workers = max(0, readers) + max(0, writers)
    if max_workers > 0:
        with futures.ThreadPoolExecutor(max_workers=max_workers) as e:
            count = 0
            for _i in range(0, readers):
                e.submit(read_func, count)
                count += 1
            for _i in range(0, writers):
                e.submit(write_func, count)
                count += 1

    writer_times = []
    reader_times = []
    for (lock_type, start, stop) in list(start_stops):
        if lock_type == lock.WRITER:
            writer_times.append((start, stop))
        else:
            reader_times.append((start, stop))
    return writer_times, reader_times


def _daemon_thread(target):
    t = threading.Thread(target=target)
    t.daemon = True
    return t


def test_no_double_writers():
    lock = fasteners.ReaderWriterLock()
    watch = _utils.StopWatch(duration=5)
    watch.start()
    dups = collections.deque()
    active = collections.deque()

    def acquire_check(me):
        with lock.write_lock():
            if len(active) >= 1:
                dups.append(me)
                dups.extend(active)
            active.append(me)
            try:
                time.sleep(random.random() / 100)
            finally:
                active.remove(me)

    def run():
        me = threading.current_thread()
        while not watch.expired():
            acquire_check(me)

    threads = []
    for i in range(0, THREAD_COUNT):
        t = _daemon_thread(run)
        threads.append(t)
        t.start()
    while threads:
        t = threads.pop()
        t.join()

    assert not dups
    assert not active


def test_no_concurrent_readers_writers():
    lock = fasteners.ReaderWriterLock()
    watch = _utils.StopWatch(duration=5)
    watch.start()
    dups = collections.deque()
    active = collections.deque()

    def acquire_check(me, reader):
        if reader:
            lock_func = lock.read_lock
        else:
            lock_func = lock.write_lock
        with lock_func():
            if not reader:
                # There should be no-one else currently active, if there
                # is ensure we capture them so that we can later blow-up
                # the test.
                if len(active) >= 1:
                    dups.append(me)
                    dups.extend(active)
            active.append(me)
            try:
                time.sleep(random.random() / 100)
            finally:
                active.remove(me)

    def run():
        me = threading.current_thread()
        while not watch.expired():
            acquire_check(me, random.choice([True, False]))

    threads = []
    for i in range(0, THREAD_COUNT):
        t = _daemon_thread(run)
        threads.append(t)
        t.start()
    while threads:
        t = threads.pop()
        t.join()

    assert not dups
    assert not active


def test_writer_abort():
    lock = fasteners.ReaderWriterLock()
    assert lock.owner is None

    with pytest.raises(RuntimeError):
        with lock.write_lock():
            assert lock.owner == lock.WRITER
            raise RuntimeError("Broken")

    assert lock.owner is None


def test_reader_abort():
    lock = fasteners.ReaderWriterLock()
    assert lock.owner is None

    with pytest.raises(RuntimeError):
        with lock.read_lock():
            assert lock.owner == lock.READER
            raise RuntimeError("Broken")

    assert lock.owner is None


def test_double_reader_abort():
    lock = fasteners.ReaderWriterLock()
    activated = collections.deque()

    def double_bad_reader():
        with lock.read_lock():
            with lock.read_lock():
                raise RuntimeError("Broken")

    def happy_writer():
        with lock.write_lock():
            activated.append(lock.owner)

    with futures.ThreadPoolExecutor(max_workers=20) as e:
        for i in range(0, 20):
            if i % 2 == 0:
                e.submit(double_bad_reader)
            else:
                e.submit(happy_writer)

    assert sum(a == 'w' for a in activated) == 10


def test_double_reader_writer():
    lock = fasteners.ReaderWriterLock()
    activated = collections.deque()
    active = threading.Event()

    def double_reader():
        with lock.read_lock():
            active.set()
            while not lock.has_pending_writers:
                time.sleep(0.001)
            with lock.read_lock():
                activated.append(lock.owner)

    def happy_writer():
        with lock.write_lock():
            activated.append(lock.owner)

    reader = _daemon_thread(double_reader)
    reader.start()
    active.wait(WAIT_TIMEOUT)
    assert active.is_set()

    writer = _daemon_thread(happy_writer)
    writer.start()

    reader.join()
    writer.join()
    assert list(activated) == ['r', 'w']


def test_reader_chaotic():
    lock = fasteners.ReaderWriterLock()
    activated = collections.deque()

    def chaotic_reader(blow_up):
        with lock.read_lock():
            if blow_up:
                raise RuntimeError("Broken")
            else:
                activated.append(lock.owner)

    def happy_writer():
        with lock.write_lock():
            activated.append(lock.owner)

    with futures.ThreadPoolExecutor(max_workers=20) as e:
        for i in range(0, 20):
            if i % 2 == 0:
                e.submit(chaotic_reader, blow_up=bool(i % 4 == 0))
            else:
                e.submit(happy_writer)

    assert sum(a == 'w' for a in activated) == 10
    assert sum(a == 'r' for a in activated) == 5


def test_writer_chaotic():
    lock = fasteners.ReaderWriterLock()
    activated = collections.deque()

    def chaotic_writer(blow_up):
        with lock.write_lock():
            if blow_up:
                raise RuntimeError("Broken")
            else:
                activated.append(lock.owner)

    def happy_reader():
        with lock.read_lock():
            activated.append(lock.owner)

    with futures.ThreadPoolExecutor(max_workers=20) as e:
        for i in range(0, 20):
            if i % 2 == 0:
                e.submit(chaotic_writer, blow_up=bool(i % 4 == 0))
            else:
                e.submit(happy_reader)

    assert sum(a == 'w' for a in activated) == 5
    assert sum(a == 'r' for a in activated) == 10


def test_writer_reader_writer():
    lock = fasteners.ReaderWriterLock()
    with lock.write_lock():
        assert lock.is_writer()
        with lock.read_lock():
            assert lock.is_reader()
            with lock.write_lock():
                assert lock.is_writer()


def test_single_reader_writer():
    results = []
    lock = fasteners.ReaderWriterLock()
    with lock.read_lock():
        assert lock.is_reader()
        assert not results
    with lock.write_lock():
        results.append(1)
        assert lock.is_writer()
    with lock.read_lock():
        assert lock.is_reader()
        assert len(results) == 1
    assert not lock.is_reader()
    assert not lock.is_writer()


def test_reader_to_writer():
    lock = fasteners.ReaderWriterLock()

    with lock.read_lock():
        with pytest.raises(RuntimeError):
            with lock.write_lock():
                pass
        assert lock.is_reader()
        assert not lock.is_writer()

    assert not lock.is_reader()
    assert not lock.is_writer()


def test_writer_to_reader():
    lock = fasteners.ReaderWriterLock()

    with lock.write_lock():

        with lock.read_lock():
            assert lock.is_writer()
            assert lock.is_reader()

        assert lock.is_writer()
        assert not lock.is_reader()

    assert not lock.is_writer()
    assert not lock.is_reader()


def test_double_writer():
    lock = fasteners.ReaderWriterLock()

    with lock.write_lock():
        assert not lock.is_reader()
        assert lock.is_writer()

        with lock.write_lock():
            assert lock.is_writer()

        assert lock.is_writer()

    assert not lock.is_reader()
    assert not lock.is_writer()


def test_double_reader():
    lock = fasteners.ReaderWriterLock()

    with lock.read_lock():
        assert lock.is_reader()
        assert not lock.is_writer()

        with lock.read_lock():
            assert lock.is_reader()

        assert lock.is_reader()

    assert not lock.is_reader()
    assert not lock.is_writer()


def test_multi_reader_multi_writer():
    writer_times, reader_times = _spawn_variation(10, 10)
    assert len(writer_times) == 10
    assert len(reader_times) == 10

    for (start, stop) in writer_times:
        assert _find_overlaps(reader_times, start, stop) == 0
        assert _find_overlaps(writer_times, start, stop) == 1
    for (start, stop) in reader_times:
        assert _find_overlaps(writer_times, start, stop) == 0


def test_multi_reader_single_writer():
    writer_times, reader_times = _spawn_variation(9, 1)
    assert len(writer_times) == 1
    assert len(reader_times) == 9

    start, stop = writer_times[0]
    assert _find_overlaps(reader_times, start, stop) == 0


def test_multi_writer():
    writer_times, reader_times = _spawn_variation(0, 10)
    assert len(writer_times) == 10
    assert len(reader_times) == 0

    for (start, stop) in writer_times:
        assert _find_overlaps(writer_times, start, stop) == 1
