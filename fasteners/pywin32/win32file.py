from ctypes import POINTER
from ctypes import pointer
from ctypes import windll
from ctypes.wintypes import BOOL
from ctypes.wintypes import DWORD
from ctypes.wintypes import HANDLE
from ctypes.wintypes import LPCWSTR

from fasteners.pywin32.pywintypes import OVERLAPPED
from fasteners.pywin32.pywintypes import SECURITY_ATTRIBUTES

_ = pointer

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

# https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
CreateFileW = windll.kernel32.CreateFileW
CreateFileW.argtypes = [
    LPCWSTR,
    DWORD,
    DWORD,
    POINTER(SECURITY_ATTRIBUTES),
    DWORD,
    DWORD,
    HANDLE,
]
CreateFileW.restype = HANDLE

# https://docs.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = [
    HANDLE
]
CloseHandle.restype = BOOL

# Errors/flags
GetLastError = windll.kernel32.GetLastError
