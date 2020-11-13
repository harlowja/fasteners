from ctypes import addressof
from ctypes import c_ubyte
from ctypes import c_void_p
from ctypes import sizeof
from ctypes import Structure
from ctypes import Union
from ctypes.wintypes import BOOL
from ctypes.wintypes import DWORD
from ctypes.wintypes import HANDLE

# Definitions for OVERLAPPED.
# Refer: https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
from ctypes.wintypes import USHORT


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


# Definition for SECURITY_ATTRIBUTES.
# Refer: https://docs.microsoft.com/en-us/previous-versions/windows/desktop/legacy/aa379560(v=vs.85)

class SecurityDescriptor(Structure):
    SECURITY_DESCRIPTOR_CONTROL = USHORT
    REVISION = 1

    _fields_ = [
        ('Revision', c_ubyte),
        ('Sbz1', c_ubyte),
        ('Control', SECURITY_DESCRIPTOR_CONTROL),
        ('Owner', c_void_p),
        ('Group', c_void_p),
        ('Sacl', c_void_p),
        ('Dacl', c_void_p),

    ]


class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [
        ('nLength', DWORD),
        ('lpSecurityDescriptor', c_void_p),
        ('bInheritHandle', BOOL)
    ]

    def __init__(self,
                 securityDescriptor,
                 bInheritHandle=BOOL(1)):
        super().__init__()
        self.securityDescriptor = securityDescriptor
        self.lpSecurityDescriptor = addressof(self.securityDescriptor)
        self.nLength = sizeof(SECURITY_ATTRIBUTES)
        self.bInheritHandle = bInheritHandle
