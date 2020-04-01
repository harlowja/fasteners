Fasteners
=========

.. image:: https://travis-ci.org/harlowja/fasteners.png?branch=master
   :target: https://travis-ci.org/harlowja/fasteners

.. image:: https://ci.appveyor.com/api/projects/status/7d7aku32pimpadiv
   :target: https://ci.appveyor.com/project/JoshuaHarlow/fasteners

.. image:: https://readthedocs.org/projects/fasteners/badge/?version=latest
   :target: https://readthedocs.org/projects/fasteners/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/dm/fasteners.svg
   :target: https://pypi.python.org/pypi/fasteners/
   :alt: Downloads

.. image:: https://img.shields.io/pypi/v/fasteners.svg
    :target: https://pypi.python.org/pypi/fasteners/
    :alt: Latest Version

Overview
--------

A python `package`_ that provides cross-platform inter-thread and inter-process
locks.

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
