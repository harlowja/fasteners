Fasteners
=========

[![Build status](https://travis-ci.org/harlowja/fasteners.png?branch=master)](https://travis-ci.org/harlowja/fasteners)
[![Documentation status](https://readthedocs.org/projects/fasteners/badge/?version=latest)](https://readthedocs.org/projects/fasteners/?badge=latest)
[![Downloads](https://img.shields.io/pypi/dm/fasteners.svg)](https://pypi.python.org/pypi/fasteners/)
[![Latest version](https://img.shields.io/pypi/v/fasteners.svg)](https://pypi.python.org/pypi/fasteners/)

Cross platform locks for threads and processes.

🔩 Install
----------

```
pip install fasteners
```

🔩 Usage
--------

Reader Writer locks for threads or processes:

```python
import fasteners

rw_lock = fasteners.ReaderWriterLock()                            # for threads
rw_lock = fasteners.InterProcessReaderWriterLock('path/to/file')  # for processes

with rw_lock.write_locked():
    ... # write_to_resource

with rw_lock.read_locked():
    ... # read_from_resource

```

Or, if you prefer using decorators:

```python
import fasteners

@fasteners.locked()
def something_for_one_thread_only():
    ...

@fasteners.interprocess_locked('path/to/file')
def something_for_one_process_only():
    ...

# works for methods as well
class SomeResource:
        
    @fasteners.read_locked()
    def read_resource(self):
        ...

    @fasteners.write_locked()
    def write_resource(self):
        ...

# same for processes:
# @fasteners.interprocess_locked
# @fasteners.interprocess_read_locked
# @fasteners.interprocess_write_locked
```

🔩 Overview
-----------

It includes the following:

Inter-thread locking decorator
******************************

* Helpful ``locked`` decorator (that acquires instance
  objects lock(s) and acquires on method entry and
  releases on method exit).

Inter-thread reader writer locks
********************************

* Multiple readers (at the same time).
* Single writer (blocking any readers).
* Helpful ``read_locked`` and ``write_locked`` decorators.

Inter-process locking decorator
*******************************

* Single process lock using a file based locking that automatically
  release on process exit (even if ``__release__`` or
  ``__exit__`` is never called).
* Helpful ``interprocess_locked`` decorator.

Inter-process reader writer lock
********************************

* Multiple readers (at the same time)
* Singer writer (blokcing any readers)
* Can be used via ``interprocess_read_locked`` and ``interprocess_write_locked``
  decorators, or ``read_lock`` and ``write_lock`` context managers.
* Based on fcntl (Linux, OSX) and LockFileEx (Windows)

Generic helpers
***************

* A ``try_lock`` helper context manager that will attempt to
  acquire a given lock and provide back whether the attempt
  passed or failed (if it passes, then further code in the
  context manager will be ran **with** the lock acquired).

.. _package: https://pypi.python.org/pypi/fasteners
