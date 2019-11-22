"""
Exposes the minimal amount of code to use Win32 native file locking. We only
need two APIs, so this is far lighter weight than pulling in all of pywin32.
"""

import os

if os.name != 'nt':
    raise RuntimeError(
        'fasteners._win32_lockapi is only importable on Windows')

import msvcrt
from ctypes import Structure, Union, windll, c_void_p, pointer, POINTER
from ctypes.wintypes import DWORD, HANDLE, BOOL


# Definitions for OVERLAPPED.
# Refer: https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
class _DummyStruct(Structure):
    _fields_ = [
        ('Offset', DWORD),
        ('OffsetHigh', DWORD),
    ]


class _DummyUnion(Union):
    _fields_ = [
        ('_offsets', _DummyStruct),
        ('Pointer', c_void_p),
    ]


class OVERLAPPED(Structure):
    _fields_ = [
        ('Internal', c_void_p),
        ('InternalHigh', c_void_p),
        ('_offset_or_ptr', _DummyUnion),
        ('hEvent', HANDLE),
    ]


# Refer: https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex
LockFileEx = windll.kernel32.LockFileEx
LockFileEx.argtypes = [
    HANDLE,
    DWORD,
    DWORD,
    DWORD,
    DWORD,
    POINTER(OVERLAPPED),
]
LockFileEx.restype = BOOL

# Refer: https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-unlockfile
UnlockFileEx = windll.kernel32.UnlockFileEx
UnlockFileEx.argtypes = [
    HANDLE,
    DWORD,
    DWORD,
    DWORD,
    POINTER(OVERLAPPED),
]
UnlockFileEx.restype = BOOL

# Errors/flags
GetLastError = windll.kernel32.GetLastError
LOCKFILE_EXCLUSIVE_LOCK = 0x02
LOCKFILE_FAIL_IMMEDIATELY = 0x01
ERROR_IO_PENDING = 997


def get_win_handle(fd):
    """
    Given a file or file descriptor, obtain the `HANDLE` to which it corresponds
    """
    if hasattr(fd, 'fileno'):
        fd = fd.fileno()
    return msvcrt.get_osfhandle(fd)
