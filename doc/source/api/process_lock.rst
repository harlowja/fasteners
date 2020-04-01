==============
 Process lock
==============

Fasteners inter-process locks are cross-platform and are released automatically
if the process crashes. They are based on the platform specific locking
mechanisms:

* fcntl for posix (Linux and OSX)
* LockFileEx (via pywin32) and \_locking (via msvcrt) for Windows

The intersection of fcntl and LockFileEx features is quite small, hence you
should always assume that:

* Locks are advisory. They do not prevent the modification of the locked file
  by other processes.

* Locks can be unintentionally released by simply opening and closing the file
  descriptor, so lock files must be accessed only using provided abstractions.

* Locks are not reentrant_. An attempt to acquire a lock multiple times can
  result in a deadlock or a crash upon a release of the lock.

* Reader writer locks are not upgradeable_. An attempt to get a reader's lock
  while holding a writer's lock (or vice versa) can result in a deadlock or a
  crash upon a release of the lock.

* There are no guarantees regarding usage by multiple threads in a
  single process. The locks work only between processes.

To learn more about the complications of locking on different platforms we
recommend the following resources:

* `File locking in Linux (blog post)`_

* `On the Brokenness of File Locking (blog post)`_

* `Everything you never wanted to know about file locking`_

* `Windows NT Files -- Locking (pywin32 docs)`_

* `_locking (Windows Dev Center)`_

* `LockFileEx function (Windows Dev Center)`_

.. _upgradeable: https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock#Upgradable_RW_lock>
.. _reentrant: https://en.wikipedia.org/wiki/Reentrant_mutex
.. _File locking in Linux (blog post): https://gavv.github.io/articles/file-locks/
.. _On the Brokenness of File Locking (blog post): http://0pointer.de/blog/projects/locking.html
.. _Windows NT Files -- Locking (pywin32 docs): http://timgolden.me.uk/pywin32-docs/Windows_NT_Files_.2d.2d_Locking.html
.. _\_locking (Windows Dev Center): https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/locking?view=vs-2019
.. _LockFileEx function (Windows Dev Center): https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex
.. _Everything you never wanted to know about file locking: https://chris.improbable.org/2010/12/16/everything-you-never-wanted-to-know-about-file-locking/

-------
Classes
-------

.. autoclass:: fasteners.process_lock.InterProcessLock
   :members:

.. autoclass:: fasteners.process_lock._InterProcessLock
   :members:

.. autoclass:: fasteners.process_lock.InterProcessReaderWriterLock
   :members:

.. autoclass:: fasteners.process_lock._InterProcessReaderWriterLock
   :members:


----------
Decorators
----------

.. autofunction:: fasteners.process_lock.interprocess_locked

.. autofunction:: fasteners.process_lock.interprocess_read_locked

.. autofunction:: fasteners.process_lock.interprocess_write_locked
