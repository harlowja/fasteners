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
Exclusive lock for processes (same API as [threading.Lock](https://docs.python.org/3/library/threading.html#threading.Lock))
```python
import fasteners
import threading

lock = threading.Lock()                                 # for threads
lock = fasteners.InterProcessLock('path/to/lock.file')  # for processes

with lock:
    ... # access resource

# or alternatively    

lock.acquire()
... # access resource
lock.release()
```

Reader Writer lock for threads or processes:

```python
import fasteners

rw_lock = fasteners.ReaderWriterLock()                                 # for threads
rw_lock = fasteners.InterProcessReaderWriterLock('path/to/lock.file')  # for processes

with rw_lock.write_locked():
    ... # write to resource

with rw_lock.read_locked():
    ... # read from resource

# or alternatively

rw_lock.acquire_read_lock()
... # read from resource
rw_lock.release_read_lock()

rw_lock.acquire_write_lock()
... # write to resource
rw_lock.release_write_lock()
```

🔩 Overview
-----------

### Process locks

The `fasteners.InterProcessLock` uses [fcntl](https://man7.org/linux/man-pages/man2/fcntl.2.html) on Unix-like systems and 
msvc [_locking](https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/locking?view=msvc-160) on Windows. 
As a result, if used cross-platform it guarantees an intersection of their features:

| lock | reentrant | mandatory |
|------|-----------|-----------|
| fcntl                        | ✘ | ✘ |
| _locking                     | ✔ | ✔ |
| fasteners.InterProcessLock   | ✘ | ✘ |


The `fasteners.InterProcessReaderWriterLock` also uses fcntl on Unix-like systems and 
[LockFileEx](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex) on Windows. Their 
features are as follows:

| lock | reentrant | mandatory | upgradable | preference | 
|------|-----------|-----------|------------|------------|
| fcntl                                    | ✘ | ✘ | ✔ | reader |
| LockFileEx                               | ✔ | ✔ | ✘ | reader |
| fasteners.InterProcessReaderWriterLock   | ✘ | ✘ | ✘ | reader |


### Thread locks

Fasteners do not provide a simple thread lock, but for the sake of comparison note that the `threading` module
provides both a reentrant and non-reentrant locks:

| lock | reentrant | mandatory |
|------|-----------|-----------|
| threading.Lock  | ✘ | ✘ |
| threading.RLock | ✔ | ✘ |


The `fasteners.ReaderWriterLock` at the moment is as follows:

| lock | reentrant | mandatory | upgradable | preference | 
|------|-----------|-----------|-------------|------------|
| fasteners.ReaderWriterLock | ✔ | ✘ | ✘ | reader |
