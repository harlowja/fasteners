"""
Implements locking utilities, including filesystem-based OS-assisted
shared/exclusive advisory locking.
"""

import ctypes
import errno
import os
from contextlib import contextmanager

from . import lock


class FileLock(object):
    """
    Implements OS-supported shared and exclusive locking using the native
    platform APIs. No matter how the process is terminated, the system will
    ensure that the locks are released.

    :param path: The path to the file that represents the lock
    :param region_start: The beginning of the region in the file to lock
    :param region_length: The size of the region to be locked
    """
    def __init__(self, path, region_start=0, region_length=1):
        #: The path to the file which is used as a lock.
        self.path = path
        self.region_start = region_start
        self.region_length = region_length
        self._file = None
        if os.name == 'nt':
            self._acquire = self._acquire_nt
            self._release = self._release_nt
        else:
            self._acquire = self._acquire_unix
            self._release = self._release_unix

    def _acquire_unix(self, exclusive, block):
        # Build the flags
        import fcntl
        lk_flags = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        if not block:
            lk_flags |= fcntl.LOCK_NB
        # Obtain a new file descriptor
        assert self._file is None, 'FileLock() cannot be used recursively'
        pardir = os.path.dirname(self.path)
        if not os.path.exists(pardir):
            os.makedirs(pardir)

        file_ = open(self.path, 'wb+')
        # Take the lock
        try:
            fcntl.lockf(file_.fileno(), lk_flags, self.region_length, self.region_start)
        except OSError as exc:
            file_.close()
            if exc.errno in (errno.EAGAIN, errno.EACCES):
                # Failed to take the lock. Never reached when block=True
                return False
            # Some other exception...
            raise
        except:
            file_.close()
            raise
        # Got it!
        self._file = file_
        return True

    def _release_unix(self):
        assert self._file is not None, 'Cannot release() a lock that is not held'
        import fcntl
        fcntl.lockf(self._file.fileno(), fcntl.LOCK_UN, self.region_length, self.region_start)
        self._file.close()
        self._file = None

    def _acquire_nt(self, exclusive, block):
        assert self._file is None, 'FileLock() cannot be used recursively'

        from . import _win32_lockapi

        flags = 0
        if exclusive:
            flags |= _win32_lockapi.LOCKFILE_EXCLUSIVE_LOCK
        if not block:
            flags |= _win32_lockapi.LOCKFILE_FAIL_IMMEDIATELY

        pardir = os.path.dirname(self.path)
        if not os.path.exists(pardir):
            os.makedirs(pardir)
        file_ = open(self.path, 'wb+')
        okay = _win32_lockapi.LockFileEx(
            _win32_lockapi.get_win_handle(self._file),
            flags,
            0,
            0,
            0,
            ctypes.pointer(_win32_lockapi.OVERLAPPED()),
        )
        if not okay:
            file_.close()
            import contextlib
            last_error = _win32_lockapi.GetLastError()
            if last_error != _win32_lockapi.ERROR_IO_PENDING:
                raise OSError(last_error)
            return False
        self._file = file_
        return True

    def _release_nt(self):
        assert self._file is not None, 'Cannot release() a lock that is not held'
        from . import _win32_lockapi
        okay = _win32_lockapi.UnlockFileEx(
            _win32_lockapi.get_win_handle(self._file),
            0,
            0,
            0,
            ctypes.pointer(_win32_lockapi.OVERLAPPED()),
        )
        if not okay:
            raise OSError(_win32_lockapi.GetLastError())

        self._file.close()
        self._file = None

    def acquire_shared(self, block=True):
        """
        Acquire shared ownership.
        """
        self._acquire(exclusive=False, block=block)

    def acquire(self, block=True):
        """
        Acquire exclusive ownership.
        """
        self._acquire(exclusive=True, block=block)

    def release_shared(self):
        """
        Release shared ownership of the resource.
        """
        self._release()

    def release(self):
        """
        Release exclusive ownership of the resource.
        """
        self._release()

    def holds_lock(self):
        """
        Determine if a lock is currently held.
        """
        return self._file is not None

    def __enter__(self):
        """
        Obtain an exclusive lock.
        """
        self.acquire(block=True)

    def __exit__(self, _exc_type, _exc, _exc_tb):
        """
        Release the lock.
        """
        self.release()

    @property
    def shared(self):
        """
        Property returns a context manager that will hold a shared lock.
        """
        return lock.lock_shared(self)
