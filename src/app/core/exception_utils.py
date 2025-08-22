from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

from app.core.exceptions import AppException, InternalServerError

T = TypeVar("T")


def handle_exceptions(
    default_exception: Type[AppException] = InternalServerError,
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator to normalize unexpected exceptions into AppException variants.

    Usage:
        @handle_exceptions()
        async def service(...):
            ...

        @handle_exceptions(default_exception=ServiceUnavailable, message="Dependency failed")
        def compute(...):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                try:
                    return await func(*args, **kwargs)
                except AppException:
                    raise
                except Exception as e:
                    error_message = message or f"Error in {func.__name__}"
                    raise default_exception(detail=error_message) from e

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except AppException:
                raise
            except Exception as e:
                error_message = message or f"Error in {func.__name__}"
                raise default_exception(detail=error_message) from e

        return sync_wrapper

    return decorator


def raise_for_status(
    condition: bool,
    exception: Type[AppException],
    detail: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Raise an exception if condition is True.

    Args:
        condition: If True, raise the exception
        exception: Exception class to raise (subclass of AppException)
        detail: Custom error message
        **kwargs: Additional arguments for the exception constructor

    Example:
        raise_for_status(
            user is None,
            ResourceNotFound,
            resource_type="User",
            resource_id=user_id
        )
    """
    if condition:
        if detail is not None:
            kwargs["detail"] = detail
        raise exception(**kwargs)
