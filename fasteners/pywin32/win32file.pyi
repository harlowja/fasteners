import sys
from ctypes import _CData, _Pointer, pointer
from typing import List, Type, TypeVar
from typing_extensions import Protocol

from fasteners.pywin32.pywintypes import OVERLAPPED

_CDataT = TypeVar("_CDataT", bound=_CData)

class _LockFileEx(Protocol):
    argtypes: List[Type[_CData]]
    restype: Type[_CData]

    def __call__(
        self,
        handle: int,
        flags: int,
        reserved: int,
        bytes_low: int,
        bytes_high: int,
        overlapped: _Pointer[OVERLAPPED],
    ) -> int: ...

class _UnlockFileEx(Protocol):
    argtypes: List[Type[_CData]]
    restype: Type[_CData]

    def __call__(
        self,
        handle: int,
        reserved: int,
        bytes_low: int,
        bytes_high: int,
        overlapped: _Pointer[OVERLAPPED],
    ) -> int: ...

class _GetLastError(Protocol):
    def __call__(self) -> int: ...

class _Kernel32(Protocol):
    LockFileEx: _LockFileEx
    UnlockFileEx: _UnlockFileEx
    GetLastError: _GetLastError

if sys.platform == "win32":
    from ctypes import WinDLL as _WinDLL

    kernel32: _WinDLL
else:
    kernel32: _Kernel32

def _(obj: _CDataT) -> _Pointer[_CDataT]: ...
LockFileEx: _LockFileEx
UnlockFileEx: _UnlockFileEx
GetLastError: _GetLastError
ERROR_LOCK_VIOLATION: int
