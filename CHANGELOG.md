# ChangeLog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

## [0.20]
  - InterProcessLock now catches OSError and handles BlockingIOError correctly.
  - Remove support for python 3.8, python 3.9 and pypy 3.9. It should still work,
    but is no longer tested.
  - Add support for python 3.12, 3.13 and pypy 3.11.

## [0.19]
  - Add `.acquire_read_lock`, `.release_read_lock`, `.acquire_write_lock`, and
    `.release_write_lock` methods to the inter thread `ReaderWriterLock` as was 
    promised in the README.
  - Remove support for python 3.7 and pypy 3.7. It should still work, but is no
    longer tested.
  - Add support for pypy 3.10 and python 3.11

## [0.18]
  - Reshuffle the process lock code and properly document it.
  - Revamp the docs and switch from sphinx to mkdocs
  - Remove difficult to use tread lock features from docs
  - Bring back support for eventlet `spawn_n`
  - Remove support for python3.6. It should still work, but is no longer tested.

## [0.17.3]:
  - Allow writer to become a reader in thread ReaderWriter lock

## [0.17.2]:
  - Remove unnecessary setuptools pin

## [0.17.1]:
  - Switch to the modern python package build infrastructure

## [0.17]: [NEVER RELEASED]
  - Remove support for python 3.5 and earlier, including 2.7
  - Add support for python 3.9 and 3.10
  - Fix a conflict with django lock
  - Add `__version__` and `__all__` attributes
  - Fix a failure to parse README as utf-8
  - Move from nosetest to pytest and cleanup testing infrastructure

## [0.16.3]:
  - Fix a failure to parse README as utf-8 on python2

## [0.16.2]:
  - Fix a failure to parse README as utf-8

## [0.16.1]: [YANKED]

## [0.16]:
  - Move from travis and appveyor to github actions
  - Add interprocess reader writer lock
  - Improve README
  - remove unused eventlet import
  - use stdlib monotonic instead of external for python >= 3.4

## [0.15]:
  - Add testing for additional python versions
  - Remove python 2.6 support
  - Remove eventlet dependency and use
    threading.current_thread instead

## [0.14]:
  - Allow providing a custom exception logger to 'locked' decorator
  - Allow providing a custom logger to process lock class
  - Fix issue #12

## [0.13]:
  - Fix 'ensure_tree' check on freebsd

## [0.12]:
  - Use a tiny retry util helper class for performing process locking retries.

## [0.11]:
  - Directly use monotonic.monotonic.
  - Use BLATHER level for previously INFO/DEBUG statements.

## [0.10]:
  - Add LICENSE in generated source tarballs
  - Add a version.py file that can be used to extract the current version.

## [0.9]:
  - Allow providing a non-standard (eventlet or other condition class) to the 
    r/w lock for cases where it is useful to do so.
  - Instead of having the r/w lock take a find eventlet keyword argument, allow 
    for it to be provided a function that will be later called to get the 
    current thread. This allows for the current *hack* to be easily removed
    by users (if they so desire).

## [0.8]:
  - Add fastener logo (from openclipart).
  - Ensure r/w writer -> reader -> writer lock acquisition.
  - Attempt to use the monotonic pypi module if its installed for monotonically 
    increasing time on python versions where this is not built-in.

## [0.7]:
  - Add helpful `locked` decorator that can lock a method using a found 
    attribute (a lock object or list of lock objects) in the instance the method 
    is attached to.
  - Expose top level `try_lock` function.

## [0.6]:
  - Allow the sleep function to be provided (so that various alternatives other 
    than time.sleep can be used), ie eventlet.sleep (or other).
  - Remove dependency on oslo.utils (replace with small utility code that 
    achieves the same effect).

## [0.5]:
  - Make it possible to provide an acquisition timeout to the interprocess lock 
    (which when acquisition can not complete in the desired time will return
    false).

## [0.4]:
  - Have the interprocess lock acquire take a blocking keyword argument 
    (defaulting to true) that can avoid blocking trying to acquire the lock

## [0.3]:
  - Renamed from 'shared_lock' to 'fasteners'

## [0.2.1]
  - Fix delay not working as expected

## [0.2]:
  - Add a interprocess lock

## [0.1]:
  - Add travis yaml file
  - Initial commit/import
