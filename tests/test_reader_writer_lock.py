from multiprocessing import Pool
from multiprocessing import Process
import os
from pathlib import Path
import random
import shutil
import tempfile
import time

from diskcache import Cache
from diskcache import Deque
import more_itertools as mo
import pytest

from fasteners.process_lock import InterProcessReaderWriterLock as ReaderWriterLock

PROCESS_COUNT = 20


@pytest.fixture()
def lock_file():
    lock_file_ = tempfile.NamedTemporaryFile()
    lock_file_.close()
    yield lock_file_.name
    try:
        os.remove(lock_file_.name)
    except OSError:
        pass


@pytest.fixture()
def disk_cache_dir():
    disk_cache_dir_ = tempfile.mkdtemp()
    yield disk_cache_dir_
    shutil.rmtree(disk_cache_dir_)


def test_lock(lock_file):
    with ReaderWriterLock(lock_file).write_lock():
        pass

    with ReaderWriterLock(lock_file).read_lock():
        pass


def no_concurrent_writers(disk_cache_dir, lock_file):
    with Cache(disk_cache_dir) as dc_:
        for _ in range(10):
            with ReaderWriterLock(lock_file).write_lock():
                if dc_.get('active_count', 0) >= 1:
                    dc_.incr('dups_count')
                dc_.incr('active_count')
                time.sleep(random.random() / 1000)
                dc_.decr('active_count')
                dc_.incr('visited_count')


def test_no_concurrent_writers(lock_file, disk_cache_dir):
    pool = Pool(PROCESS_COUNT)
    pool.starmap(no_concurrent_writers, [(disk_cache_dir, lock_file)] * PROCESS_COUNT,
                 chunksize=1)

    with Cache(disk_cache_dir) as dc:
        assert dc.get('active_count') == 0
        assert dc.get('dups_count') == None
        assert dc.get('visited_count') == 10 * PROCESS_COUNT


def no_concurrent_readers_writers(disk_cache_dir, lock_file):
    with Cache(disk_cache_dir) as dc_:
        for _ in range(10):
            reader = random.choice([True, False])
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


def test_no_concurrent_readers_writers(lock_file, disk_cache_dir):
    pool = Pool(PROCESS_COUNT)
    pool.starmap(no_concurrent_readers_writers, [(disk_cache_dir, lock_file)] * PROCESS_COUNT,
                 chunksize=1)

    with Cache(disk_cache_dir) as dc:
        assert dc.get('active_count') == 0
        assert dc.get('dups_count') is None
        assert dc.get('visited_count') == 10 * PROCESS_COUNT


def run_doesnt_hang(disk_cache_dir, lock_file, type_):
    lock = (ReaderWriterLock(lock_file).write_lock if type_ == 'w' else
            ReaderWriterLock(lock_file).read_lock)
    with lock():
        with Cache(disk_cache_dir) as dc_:
            dc_.incr(type_)


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


def test_reader_releases_lock_upon_crash(disk_cache_dir, lock_file):
    p1 = Process(target=reader_releases_lock_upon_crash_reader_lock,
                 args=(disk_cache_dir, lock_file, 1))
    p2 = Process(target=reader_releases_lock_upon_crash_writer_lock,
                 args=(disk_cache_dir, lock_file, 2))

    p1.start()
    p1.join()

    p2.start()
    p2.join()

    with Cache(disk_cache_dir) as dc:
        assert dc.get('pid1') != dc.get('pid2')

    assert p1.exitcode != 0
    assert p2.exitcode == 0


def writer_releases_lock_upon_crash(disk_cache_dir, lock_file, i, crash):
    ReaderWriterLock(lock_file).acquire_write_lock(timeout=5)
    with Cache(disk_cache_dir) as dc_:
        dc_.set('pid{}'.format(i), os.getpid())
    if crash:
        raise RuntimeError('')


def test_writer_releases_lock_upon_crash(lock_file, disk_cache_dir):
    p1 = Process(target=writer_releases_lock_upon_crash,
                 args=(disk_cache_dir, lock_file, 1, True))
    p2 = Process(target=writer_releases_lock_upon_crash,
                 args=(disk_cache_dir, lock_file, 2, False))

    p1.start()
    p1.join()

    p2.start()
    p2.join()

    with Cache(disk_cache_dir) as dc:
        assert dc.get('pid1') != dc.get('pid2')

    assert p1.exitcode != 0
    assert p2.exitcode == 0


def _spawn_variation(disk_cache_dir, lock_file, readers, writers):
    visits = Deque(directory=str(disk_cache_dir / 'w'))
    pool = Pool(readers + writers)
    pool.starmap(_spawling, [(lock_file, visits, type_) for type_ in ['w'] * writers + ['r'] * readers])
    return visits


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


def _assert_valid(visits):
    """Check if writes dont overlap other writes and reads"""

    # check that writes open and close consequently
    write_blocks = mo.split_at(visits, lambda x: x[1] == 'r')
    for write_block in write_blocks:
        for v1, v2 in mo.chunked(write_block, 2):
            assert v1[0] == v2[0]

    # check that reads open and close in groups between writes
    read_blocks = mo.split_at(visits, lambda x: x[1] == 'w')
    for read_block in read_blocks:
        for v1, v2 in mo.chunked(sorted(read_block), 2):
            assert v1[0] == v2[0]


def test_multi_reader_multi_writer(lock_file, disk_cache_dir):
    visits = _spawn_variation(Path(disk_cache_dir),
                              Path(lock_file), 10, 10)

    assert len(visits) == 20 * 2
    _assert_valid(visits)


def test_multi_reader_single_writer(lock_file, disk_cache_dir):
    visits = _spawn_variation(Path(disk_cache_dir),
                              Path(lock_file), 9, 1)

    assert len(visits) == 10 * 2
    _assert_valid(visits)


def test_multi_writer(lock_file, disk_cache_dir):
    visits = _spawn_variation(Path(disk_cache_dir),
                              Path(lock_file), 0, 10)

    assert len(visits) == 10 * 2
    _assert_valid(visits)
