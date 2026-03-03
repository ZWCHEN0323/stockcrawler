from __future__ import annotations

from typing import Callable, TypeVar, Any

import backoff

from app.utils.logger import logger


T = TypeVar("T")


def with_backoff(
    max_tries: int = 3,
    base: float = 1.0,
    factor: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @backoff.on_exception(
            backoff.expo,
            Exception,
            max_tries=max_tries,
            base=base,
            factor=factor,
        )
        def wrapped(*args: Any, **kwargs: Any) -> T:
            logger.debug("Calling %s with backoff", func.__name__)
            return func(*args, **kwargs)

        return wrapped

    return decorator

