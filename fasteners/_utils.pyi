import logging
from types import TracebackType
from typing import Callable, List, Optional, Type, TypeVar
from typing_extensions import ParamSpec, Protocol

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T")
_StopWatchT = TypeVar("_StopWatchT", bound="StopWatch")

class _Lock(Protocol):
    def acquire(self) -> bool: ...
    def release(self) -> None: ...

class _Watch(Protocol):
    def leftover(self) -> Optional[float]: ...

BLATHER: int
LOG: logging.Logger

def canonicalize_path(path: object) -> bytes: ...
def pick_first_not_none(*values: Optional[_T]) -> Optional[_T]: ...

class LockStack:
    _stack: List[_Lock]
    _logger: logging.Logger

    def __init__(self, logger: Optional[logging.Logger] = ...) -> None: ...
    def acquire_lock(self, lock: _Lock) -> bool: ...
    def __enter__(self) -> LockStack: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...

class RetryAgain(Exception): ...

class Retry:
    delay: float
    attempts: int
    max_delay: float
    sleep_func: Callable[[float], None]
    watch: Optional[_Watch]

    def __init__(
        self,
        delay: float,
        max_delay: float,
        sleep_func: Callable[[float], None] = ...,
        watch: Optional[_Watch] = ...,
    ) -> None: ...
    def __call__(
        self, fn: Callable[_P, _R], *args: _P.args, **kwargs: _P.kwargs
    ) -> _R: ...

class StopWatch:
    duration: Optional[float]
    started_at: Optional[float]
    stopped_at: Optional[float]

    def __init__(self, duration: Optional[float] = ...) -> None: ...
    def leftover(self) -> Optional[float]: ...
    def elapsed(self) -> float: ...
    def __enter__(self: _StopWatchT) -> _StopWatchT: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...
    def start(self) -> None: ...
    def expired(self) -> bool: ...
