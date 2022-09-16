"""
These tests need to run in child processes, otherwise eventlet monkey_patch
conflicts with multiprocessing and other tests fail.
"""
import concurrent.futures
from multiprocessing import get_context


def _test_eventlet_spawn_n_bug():
    """Both threads run at the same time thru the lock"""
    import eventlet
    eventlet.monkey_patch()
    from fasteners import ReaderWriterLock

    STARTED = eventlet.event.Event()
    FINISHED = eventlet.event.Event()
    lock = ReaderWriterLock()

    def other():
        STARTED.send('started')
        with lock.write_lock():
            FINISHED.send('finished')

    with lock.write_lock():
        eventlet.spawn_n(other)
        STARTED.wait()
        assert FINISHED.wait(1) == 'finished'


def _test_eventlet_spawn_n_bugfix():
    """Threads wait for each other as they should"""
    import eventlet
    eventlet.monkey_patch()
    from fasteners import ReaderWriterLock

    STARTED = eventlet.event.Event()
    FINISHED = eventlet.event.Event()
    lock = ReaderWriterLock(current_thread_functor=eventlet.getcurrent)

    def other():
        STARTED.send('started')
        with lock.write_lock():
            FINISHED.send('finished')

    with lock.write_lock():
        eventlet.spawn_n(other)
        STARTED.wait()
        assert FINISHED.wait(1) is None

    assert FINISHED.wait(1) == 'finished'


def test_eventlet_spawn_n_bug():
    with concurrent.futures.ProcessPoolExecutor(mp_context=get_context('spawn')) as executor:
        f = executor.submit(_test_eventlet_spawn_n_bug)
        f.result()


def test_eventlet_spawn_n_bugfix():
    with concurrent.futures.ProcessPoolExecutor(mp_context=get_context('spawn')) as executor:
        f = executor.submit(_test_eventlet_spawn_n_bugfix)
        f.result()
