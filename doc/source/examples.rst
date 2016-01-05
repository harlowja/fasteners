Examples
========

------------------
Interprocess locks
------------------

.. note::

  Launch multiple of these at the same time to see the lock(s) in action.

.. code-block:: python

    import time

    import fasteners

    @fasteners.interprocess_locked('/tmp/tmp_lock_file')
    def test():
        for i in range(10):
            print('I have the lock')
            time.sleep(1)

    print('Waiting for the lock')
    test()

.. code-block:: python

    import time

    import fasteners

    def test():
        for i in range(10):
            with fasteners.InterProcessLock('/tmp/tmp_lock_file'):
                print('I have the lock')
                time.sleep(1)

    test()

.. code-block:: python

    import time

    import fasteners

    def test():
        a_lock = fasteners.InterProcessLock('/tmp/tmp_lock_file')
        for i in range(10):
            gotten = a_lock.acquire(blocking=False)
            try:
                if gotten:
                    print('I have the lock')
                    time.sleep(0.2)
                else:
                    print('I do not have the lock')
                    time.sleep(0.1)
            finally:
                if gotten:
                    a_lock.release()

    test()

----------------------------
Reader/writer (shared) locks
----------------------------

.. code-block:: python

    import random
    import threading
    import time

    import fasteners

    def read_something(ident, rw_lock):
        with rw_lock.read_lock():
            print("Thread %s is reading something" % ident)
            time.sleep(1)

    def write_something(ident, rw_lock):
        with rw_lock.write_lock():
            print("Thread %s is writing something" % ident)
            time.sleep(2)

    rw_lock = fasteners.ReaderWriterLock()
    threads = []
    for i in range(0, 10):
        is_writer = random.choice([True, False])
        if is_writer:
            threads.append(threading.Thread(target=write_something,
                                            args=(i, rw_lock)))
        else:
            threads.append(threading.Thread(target=read_something,
                                            args=(i, rw_lock)))

    try:
        for t in threads:
            t.start()
    finally:
        while threads:
            t = threads.pop()
            t.join()

--------------
Lock decorator
--------------

.. code-block:: python

    import threading

    import fasteners

    class NotThreadSafeThing(object):
        def __init__(self):
            self._lock = threading.Lock()

        @fasteners.locked
        def do_something(self):
            print("Doing something in a thread safe manner")

    o = NotThreadSafeThing()
    o.do_something()

--------------------
Multi-lock decorator
--------------------

.. code-block:: python

    import threading

    import fasteners

    class NotThreadSafeThing(object):
        def __init__(self):
            self._locks = [threading.Lock(), threading.Lock()]

        @fasteners.locked(lock='_locks')
        def do_something(self):
            print("Doing something in a thread safe manner")

    o = NotThreadSafeThing()
    o.do_something()
