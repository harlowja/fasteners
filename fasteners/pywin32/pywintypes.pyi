from ctypes import Structure, Union
from typing import Optional

class _DummyStruct(Structure):
    Offset: int
    OffsetHigh: int

class _DummyUnion(Union):
    _offsets: _DummyStruct
    Pointer: Optional[int]

class OVERLAPPED(Structure):
    Internal: Optional[int]
    InternalHigh: Optional[int]
    _offset_or_ptr: _DummyUnion
    hEvent: Optional[int]
