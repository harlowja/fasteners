==============
 Process lock
==============

-------
Classes
-------

.. autoclass:: fasteners.process_lock.InterProcessLock
   :members:

.. autoclass:: fasteners.process_lock._InterProcessLock
   :members:

----------
Decorators
----------

.. autofunction:: fasteners.process_lock.interprocess_locked

.. code-block:: python
    # Launch multiple of these at the same time to see the lock in action
    import time
    import fasteners

    @fasteners.process_lock.interprocess_locked('tmp_lock_file')
    def test():
        for i in range(10):
            print('I have the lock')
            time.sleep(1)


    print('Waiting for the lock')
    test()
