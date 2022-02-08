# User Guide

## Basic Exclusive Lock Usage

Exclusive Lock for independent processes has the same API as the
[threading.Lock](https://docs.python.org/3/library/threading.html#threading.Lock)
for threads:
```python
import fasteners
import threading

lock = threading.Lock()                                 # for threads
lock = fasteners.InterProcessLock('path/to/lock.file')  # for processes

with lock:
    ... # exclusive access

# or alternatively    

lock.acquire()
... # exclusive access
lock.release()
```

## Basic Reader Writer lock usage

Reader Writer lock has a similar API, which is the same for threads or processes:

```python
import fasteners

# for threads
rw_lock = fasteners.ReaderWriterLock()                                 
# for processes
rw_lock = fasteners.InterProcessReaderWriterLock('path/to/lock.file')  

with rw_lock.write_lock():
    ... # write access

with rw_lock.read_lock():
    ... # read access

# or alternatively, for processes only:

rw_lock.acquire_read_lock()
... # read access
rw_lock.release_read_lock()

rw_lock.acquire_write_lock()
... # write access
rw_lock.release_write_lock()
```

## Advanced usage

For more details and options see [Process lock details](inter_process.md) and [Thread lock details](inter_thread.md).

