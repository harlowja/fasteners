# Glossary

To learn more about the various aspects of locks, check the wikipedia pages for
[locks](https://en.wikipedia.org/wiki/Lock_(computer_science)) and
[readers writer locks](https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock) 
Here we briefly mention the main notions used in the documentation.

* **Lock** - a mechanism that prevents two or more threads or processes from running the same code at the same time.
* **Readers writer lock** - a mechanism that prevents two or more threads from having write (or write and read) access,
  while allowing multiple readers.
* **Reentrant lock** - a lock that can be acquired (and then released) multiple times, as in:
 
    ```python
    with lock:
        with lock:
            ... # some code
    ```
  
* **Mandatory lock** (as opposed to advisory lock) - a lock that is enforced by the operating system, rather than
  by the cooperation between threads or processes
* **Upgradable readers writer lock** - a readers writer lock that can be upgraded from reader to writer (or downgraded
  from writer to reader) without losing the lock that is already held, as in:
```python
with rw_lock.read_lock():
    ... # read access
    with rw_lock.write_lock():
        ... # write access
    ... # read access
```
* **Readers writer lock preference** - describes the behaviour when multiple threads or processes are waiting for
  access. Some of the patterns are:
    * **Reader preference** - If lock is held by readers, then new readers will get immediate access. This can result
      in writers waiting forever (writer starvation).
    * **Writer preference** - If writer is waiting for a lock, then all the new readers (and writers) will be queued
      after it. This can result in readers waiting forever (reader starvation).
    * **Phase fair** - Lock that alternates between readers and writers.

