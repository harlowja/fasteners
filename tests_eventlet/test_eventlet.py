import eventlet

eventlet.monkey_patch()

from fasteners import ReaderWriterLock


def test_eventlet_spawn_n_bug():
    """Both threads run at the same time thru the lock"""
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


def test_eventlet_spawn_n_bugfix():
    """Threads wait for each other as they should"""
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
