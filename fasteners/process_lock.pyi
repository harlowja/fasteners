import logging
import os
from pathlib import Path
from types import TracebackType
from typing import Callable, ContextManager, Optional, TextIO, Type, TypeVar, Union
from typing_extensions import ParamSpec

from fasteners import _utils

_P = ParamSpec("_P")
_R = TypeVar("_R")
_InterProcessLockT = TypeVar("_InterProcessLockT", bound="InterProcessLock")
_Path = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]

LOG: logging.Logger

def _ensure_tree(path: _Path) -> bool: ...

class InterProcessLock:
    MAX_DELAY: float
    DELAY_INCREMENT: float
    lockfile: Optional[TextIO]
    path: bytes
    acquired: bool
    sleep_func: Callable[[float], None]
    logger: logging.Logger

    def __init__(
        self,
        path: Union[Path, str],
        sleep_func: Callable[[float], None] = ...,
        logger: Optional[logging.Logger] = ...,
    ) -> None: ...
    def _try_acquire(
        self, blocking: bool, watch: _utils.StopWatch
    ) -> bool: ...
    def _do_open(self) -> None: ...
    def acquire(
        self,
        blocking: bool = ...,
        delay: float = ...,
        max_delay: float = ...,
        timeout: Optional[float] = ...,
    ) -> bool: ...
    def _do_close(self) -> None: ...
    def __enter__(self: _InterProcessLockT) -> _InterProcessLockT: ...
    def release(self) -> None: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...
    def exists(self) -> bool: ...
    def trylock(self) -> None: ...
    def unlock(self) -> None: ...

class InterProcessReaderWriterLock:
    MAX_DELAY: float
    DELAY_INCREMENT: float
    lockfile: Optional[TextIO]
    path: bytes
    sleep_func: Callable[[float], None]
    logger: logging.Logger

    def __init__(
        self,
        path: Union[Path, str],
        sleep_func: Callable[[float], None] = ...,
        logger: Optional[logging.Logger] = ...,
    ) -> None: ...
    def read_lock(
        self, delay: float = ..., max_delay: float = ...
    ) -> ContextManager[None]: ...
    def write_lock(
        self, delay: float = ..., max_delay: float = ...
    ) -> ContextManager[None]: ...
    def _try_acquire(
        self,
        blocking: bool,
        watch: _utils.StopWatch,
        exclusive: bool,
    ) -> bool: ...
    def _do_open(self) -> None: ...
    def acquire_read_lock(
        self,
        blocking: bool = ...,
        delay: float = ...,
        max_delay: float = ...,
        timeout: Optional[float] = ...,
    ) -> bool: ...
    def acquire_write_lock(
        self,
        blocking: bool = ...,
        delay: float = ...,
        max_delay: float = ...,
        timeout: Optional[float] = ...,
    ) -> bool: ...
    def _acquire(
        self,
        blocking: bool = ...,
        delay: float = ...,
        max_delay: float = ...,
        timeout: Optional[float] = ...,
        exclusive: bool = ...,
    ) -> bool: ...
    def _do_close(self) -> None: ...
    def release_write_lock(self) -> None: ...
    def release_read_lock(self) -> None: ...

def interprocess_write_locked(
    path: Union[Path, str],
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
def interprocess_read_locked(
    path: Union[Path, str],
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
def interprocess_locked(
    path: Union[Path, str],
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
