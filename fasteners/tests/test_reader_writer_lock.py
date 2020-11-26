import os
import random
import shutil
import tempfile
import time
from multiprocessing import Pool
from multiprocessing import Process
from pathlib import Path

import more_itertools as mo
from diskcache import Cache
from diskcache import Deque
from six import wraps

from fasteners import test
from fasteners.process_lock import InterProcessReaderWriterLock as ReaderWriterLock

PROCESS_COUNT = 20


def unpack(func):
    @wraps(func)
    def wrapper(arg_tuple):
        return func(*arg_tuple)

    return wrapper


def run_doesnt_hang(disk_cache_dir, lock_file, type_):
    lock = (ReaderWriterLock(lock_file).write_lock if type_ == 'w' else
            ReaderWriterLock(lock_file).read_lock)
    with lock():
        with Cache(disk_cache_dir) as dc_:
            dc_.incr(type_)


@unpack
def run_no_concurrent_writers(disk_cache_dir, lock_file):
    with Cache(disk_cache_dir) as dc_:
        for _ in range(10):
            no_concurrent_writers_acquire_check(dc_, lock_file)


def no_concurrent_writers_acquire_check(dc_, lock_file):
    with ReaderWriterLock(lock_file).write_lock():
        if dc_.get('active_count', 0) >= 1:
            dc_.incr('dups_count')
        dc_.incr('active_count')
        time.sleep(random.random() / 1000)
        dc_.decr('active_count')
        dc_.incr('visited_count')


@unpack
def run_no_cuncurrent_readers_writers(disk_cache_dir, lock_file):
    with Cache(disk_cache_dir) as dc_:
        for _ in range(10):
            no_concurrent_readers_writers_acquire_check(dc_, lock_file,
                                                        random.choice([True, False]))


def no_concurrent_readers_writers_acquire_check(dc_, lock_file, reader):
    if reader:
        lock_func = ReaderWriterLock(lock_file).read_lock
    else:
        lock_func = ReaderWriterLock(lock_file).write_lock
    with lock_func():
        if not reader:
            if dc_.get('active_count', 0) >= 1:
                dc_.incr('dups_count')
        dc_.incr('active_count')
        time.sleep(random.random() / 1000)
        dc_.decr('active_count')
        dc_.incr('visited_count')


def run_reader_writer_chaotic(disk_cache_dir, lock_file, type_, blow_up):
    lock = (ReaderWriterLock(lock_file).write_lock if type_ == 'w' else
            ReaderWriterLock(lock_file).read_lock)
    with lock():
        with Cache(disk_cache_dir) as dc_:
            dc_.incr(type_)
        if blow_up:
            raise RuntimeError()


def reader_releases_lock_upon_crash_reader_lock(disk_cache_dir, lock_file, i):
    with ReaderWriterLock(lock_file).read_lock():
        with Cache(disk_cache_dir) as dc_:
            dc_.set('pid{}'.format(i), os.getpid())
        raise RuntimeError('')


def reader_releases_lock_upon_crash_writer_lock(disk_cache_dir, lock_file, i):
    ReaderWriterLock(lock_file).acquire_write_lock(timeout=5)
    with Cache(disk_cache_dir) as dc_:
        dc_.set('pid{}'.format(i), os.getpid())


def run_writer_releases_lock_upon_crash(disk_cache_dir, lock_file, i, crash):
    ReaderWriterLock(lock_file).acquire_write_lock(timeout=5)
    with Cache(disk_cache_dir) as dc_:
        dc_.set('pid{}'.format(i), os.getpid())
    if crash:
        raise RuntimeError('')


class ProcessReaderWriterLock(test.TestCase):

    def setUp(self):
        super(ProcessReaderWriterLock, self).setUp()

        lock_file = tempfile.NamedTemporaryFile()
        lock_file.close()
        self.lock_file = lock_file.name
        self.disk_cache_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(ProcessReaderWriterLock, self).tearDown()

        shutil.rmtree(self.disk_cache_dir, ignore_errors=True)
        try:
            os.remove(self.lock_file)
        except OSError:
            pass

    def test_lock(self):

        with ReaderWriterLock(self.lock_file).write_lock():
            pass

        with ReaderWriterLock(self.lock_file).read_lock():
            pass

    def test_no_concurrent_writers(self):
        pool = Pool(PROCESS_COUNT)
        pool.map(run_no_concurrent_writers, [(self.disk_cache_dir, self.lock_file)] * PROCESS_COUNT,
                 chunksize=1)

        with Cache(self.disk_cache_dir) as dc:
            self.assertEqual(dc.get('active_count'), 0)
            self.assertEqual(dc.get('dups_count'), None)
            self.assertEqual(dc.get('visited_count'), 10 * PROCESS_COUNT)

    def test_no_concurrent_readers_writers(self):
        pool = Pool(PROCESS_COUNT)
        pool.map(run_no_cuncurrent_readers_writers,
                 [(self.disk_cache_dir, self.lock_file)] * PROCESS_COUNT, chunksize=1)

        with Cache(self.disk_cache_dir) as dc:
            self.assertEqual(dc.get('active_count'), 0)
            self.assertEqual(dc.get('dups_count'), None)
            self.assertEqual(dc.get('visited_count'), 10 * PROCESS_COUNT)

    def test_writer_releases_lock_upon_crash(self):
        p1 = Process(target=run_writer_releases_lock_upon_crash,
                     args=(self.disk_cache_dir, self.lock_file, 1, True))
        p2 = Process(target=run_writer_releases_lock_upon_crash,
                     args=(self.disk_cache_dir, self.lock_file, 2, False))

        p1.start()
        p1.join()

        p2.start()
        p2.join()

        with Cache(self.disk_cache_dir) as dc:
            assert dc.get('pid1') != dc.get('pid2')

        self.assertNotEqual(0, p1.exitcode)
        self.assertEqual(0, p2.exitcode)

    def test_reader_releases_lock_upon_crash(self):
        p1 = Process(target=reader_releases_lock_upon_crash_reader_lock,
                     args=(self.disk_cache_dir, self.lock_file, 1))
        p2 = Process(target=reader_releases_lock_upon_crash_writer_lock,
                     args=(self.disk_cache_dir, self.lock_file, 2))

        p1.start()
        p1.join()

        p2.start()
        p2.join()

        with Cache(self.disk_cache_dir) as dc:
            assert dc.get('pid1') != dc.get('pid2')

        self.assertNotEqual(0, p1.exitcode)
        self.assertEqual(0, p2.exitcode)

    def test_multi_reader_multi_writer(self):
        visits = _spawn_variation(Path(self.disk_cache_dir),
                                  Path(self.lock_file), 10, 10)

        self.assertEqual(20 * 2, len(visits))
        self._assert_valid(visits)

    def test_multi_reader_single_writer(self):
        visits = _spawn_variation(Path(self.disk_cache_dir),
                                  Path(self.lock_file), 9, 1)

        self.assertEqual(10 * 2, len(visits))
        self._assert_valid(visits)

    def test_multi_writer(self):
        visits = _spawn_variation(Path(self.disk_cache_dir),
                                  Path(self.lock_file), 0, 10)

        self.assertEqual(10 * 2, len(visits))
        self._assert_valid(visits)

    def _assert_valid(self, visits):
        """Check if writes dont overlap other writes and reads"""

        # check that writes open and close consequently
        write_blocks = mo.split_at(visits, lambda x: x[1] == 'r')
        for write_block in write_blocks:
            for v1, v2 in mo.chunked(write_block, 2):
                self.assertEqual(v1[0], v2[0])

        # check that reads open and close in groups between writes
        read_blocks = mo.split_at(visits, lambda x: x[1] == 'w')
        for read_block in read_blocks:
            for v1, v2 in mo.chunked(sorted(read_block), 2):
                self.assertEqual(v1[0], v2[0])


def _spawn_variation(disk_cache_dir, lock_file, readers, writers):
    visits = Deque(directory=str(disk_cache_dir / 'w'))
    pool = Pool(readers + writers)
    pool.map(_spawling, [(lock_file, visits, type_) for type_ in ['w'] * writers + ['r'] * readers])
    return visits


@unpack
def _spawling(lock_file, visits, type_):
    lock = ReaderWriterLock(lock_file)

    if type_ == 'w':
        lock.acquire_write_lock(timeout=5)
    else:
        lock.acquire_read_lock(timeout=5)

    visits.append((os.getpid(), type_))
    time.sleep(random.random() / 100 + 0.01)
    visits.append((os.getpid(), type_))

    if type_ == 'w':
        lock.release_write_lock()
    else:
        lock.release_read_lock()
