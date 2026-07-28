from abc import ABC, abstractmethod
from typing import TextIO

class _InterProcessReaderWriterLockMechanism(ABC):
    @staticmethod
    @abstractmethod
    def trylock(lockfile: TextIO, exclusive: bool) -> bool: ...
    @staticmethod
    @abstractmethod
    def unlock(lockfile: TextIO) -> None: ...
    @staticmethod
    @abstractmethod
    def get_handle(path: bytes) -> TextIO: ...
    @staticmethod
    @abstractmethod
    def close_handle(lockfile: TextIO) -> None: ...

class _InterProcessMechanism(ABC):
    @staticmethod
    @abstractmethod
    def trylock(lockfile: TextIO) -> None: ...
    @staticmethod
    @abstractmethod
    def unlock(lockfile: TextIO) -> None: ...

class _WindowsInterProcessMechanism(_InterProcessMechanism):
    @staticmethod
    def trylock(lockfile: TextIO) -> None: ...
    @staticmethod
    def unlock(lockfile: TextIO) -> None: ...

class _FcntlInterProcessMechanism(_InterProcessMechanism):
    @staticmethod
    def trylock(lockfile: TextIO) -> None: ...
    @staticmethod
    def unlock(lockfile: TextIO) -> None: ...

class _WindowsInterProcessReaderWriterLockMechanism(
    _InterProcessReaderWriterLockMechanism
):
    @staticmethod
    def trylock(lockfile: TextIO, exclusive: bool) -> bool: ...
    @staticmethod
    def unlock(lockfile: TextIO) -> None: ...
    @staticmethod
    def get_handle(path: bytes) -> TextIO: ...
    @staticmethod
    def close_handle(lockfile: TextIO) -> None: ...

class _FcntlInterProcessReaderWriterLockMechanism(
    _InterProcessReaderWriterLockMechanism
):
    @staticmethod
    def trylock(lockfile: TextIO, exclusive: bool) -> bool: ...
    @staticmethod
    def unlock(lockfile: TextIO) -> None: ...
    @staticmethod
    def get_handle(path: bytes) -> TextIO: ...
    @staticmethod
    def close_handle(lockfile: TextIO) -> None: ...
_interprocess_reader_writer_mechanism: _InterProcessReaderWriterLockMechanism
_interprocess_mechanism: _InterProcessMechanism
