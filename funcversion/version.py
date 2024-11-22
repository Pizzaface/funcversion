from typing import Callable

from packaging.version import Version as PkgVersion, InvalidVersion

from funcversion import VersionedFunction
from funcversion.core import _version_registry, _versioned_functions_registry


def version(version_id: str) -> Callable[[Callable], VersionedFunction]:
    """
    Decorator to register a function version.

    Args:
        version_id (str): The version identifier (e.g., "1.0.0").

    Returns:
        Callable[[Callable], Callable]: The decorator function.
    """

    def decorator(func: Callable) -> Callable:
        original_func, is_classmethod, is_staticmethod = _unwrap_function(func)

        func_key = _get_function_key(original_func)

        _validate_version_id(version_id)

        _register_version(func_key, version_id, original_func)

        wrapper = _get_or_create_wrapper(func_key)

        return _reapply_method_type(wrapper, func, is_classmethod, is_staticmethod)

    return decorator


def _unwrap_function(func: Callable) -> tuple[Callable, bool, bool]:
    """
    Unwrap the function if it's a classmethod or staticmethod.

    Args:
        func (Callable): The function to unwrap.

    Returns:
        tuple[Callable, bool, bool]: The original function, is_classmethod flag, is_staticmethod flag.
    """
    is_classmethod = False
    is_staticmethod = False
    original_func = func

    if isinstance(func, classmethod):
        is_classmethod = True
        original_func = func.__func__
    elif isinstance(func, staticmethod):
        is_staticmethod = True
        original_func = func.__func__

    return original_func, is_classmethod, is_staticmethod


def _get_function_key(func: Callable) -> str:
    """
    Generate a unique key for the function based on its module and qualified name.

    Args:
        func (Callable): The function to generate a key for.

    Returns:
        str: The unique function key.
    """
    return f"{func.__module__}.{func.__qualname__}"


def _validate_version_id(version_id: str) -> None:
    """
    Validate the version identifier.

    Args:
        version_id (str): The version identifier to validate.

    Raises:
        ValueError: If the version_id is not a valid semantic version.
    """
    if not isinstance(version_id, str):
        raise ValueError(
            f"Version identifier must be a string, got {type(version_id).__name__}."
        )

    try:
        PkgVersion(version_id)
    except (InvalidVersion, TypeError) as e:
        raise ValueError(
            f"Version '{version_id}' is not a valid semantic version."
        ) from e


def _register_version(func_key: str, version_id: str, func: Callable) -> None:
    """
    Register a new version for the function.

    Args:
        func_key (str): The unique function key.
        version_id (str): The version identifier.
        func (Callable): The function implementation.

    Raises:
        ValueError: If the version is already registered.
    """
    if version_id in _version_registry[func_key]:
        raise ValueError(
            f"Version '{version_id}' is already registered for function '{func_key}'."
        )
    _version_registry[func_key][version_id] = func


def _get_or_create_wrapper(func_key: str) -> VersionedFunction:
    """
    Retrieve an existing VersionedFunction wrapper or create a new one.

    Args:
        func_key (str): The unique function key.

    Returns:
        VersionedFunction: The wrapper instance.
    """
    if func_key not in _versioned_functions_registry:
        wrapper = VersionedFunction(func_key)
        _versioned_functions_registry[func_key] = wrapper
    else:
        wrapper = _versioned_functions_registry[func_key]
    return wrapper


def _reapply_method_type(
    wrapper: VersionedFunction,
    original_func: Callable,
    is_classmethod: bool,
    is_staticmethod: bool,
) -> Callable:
    """
    Re-apply the original method type (classmethod or staticmethod) to the wrapper.

    Args:
        wrapper (VersionedFunction): The wrapper instance.
        original_func (Callable): The original function.
        is_classmethod (bool): Whether the original function was a classmethod.
        is_staticmethod (bool): Whether the original function was a staticmethod.

    Returns:
        Callable: The appropriately wrapped function.
    """
    if is_classmethod:
        return classmethod(wrapper)
    elif is_staticmethod:
        return staticmethod(wrapper)
    else:
        return wrapper  # The original function isn't used directly; the wrapper is returned to maintain versioning functionality.
