# Inter thread locks

Fasteners inter-thread locks were build specifically for the needs of 
`oslo.concurrency` project and thus have a rather peculiar API. We do not 
recommend using it fully, and it is hence not documented (but maintained until 
the end of time).

Instead, we recommend limiting the use of fasteners inter-thread readers writer
lock to the basic API:

```python
import fasteners

# for threads
rw_lock = fasteners.ReaderWriterLock()                                 

with rw_lock.write_lock():
    ... # write access

with rw_lock.read_lock():
    ... # read access
```

## (Lack of) Features

Fasteners inter-thread readers writer lock is

* not [upgradeable]. An attempt to get a reader's lock while holding a writer's 
  lock (or vice versa) will raise an exception.

* [reentrant] (!). You can acquire (and correspondingly release) the lock 
  multiple times.

* has writer preference. Readers will queue after writers and pending writers.


[upgradeable]: https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock#Upgradable_RW_lock>
[reentrant]: https://en.wikipedia.org/wiki/Reentrant_mutex
