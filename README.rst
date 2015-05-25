Fasteners
=========

.. image:: https://travis-ci.org/harlowja/fasteners.png?branch=master
   :target: https://travis-ci.org/harlowja/fasteners

Overview
--------

A python `package`_ that provides useful locks.

It includes the following.

Reader-writer locks
*******************

* Multiple readers (at the same time).
* Single writers (blocking any readers).
* Helpful ``read_locked`` and ``write_locked`` decorators.

Inter-process locks
*******************

* Single writer using file based locking (these automatically
  release on process exit, even if ``__release__`` or
  ``__exit__`` is never called).
* Helpful ``interprocess_locked`` decorator.

.. _package: https://pypi.python.org/pypi/fasteners
