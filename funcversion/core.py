# funcversion/core.py

import sys
from functools import wraps
from collections import defaultdict
from packaging.version import Version, InvalidVersion
from packaging import version as pkg_version  # For semantic versioning
import warnings
from .exceptions import VersionNotFoundError
from types import MethodType

# Global registry to store function versions
_version_registry = defaultdict(dict)

class VersionedFunction:
    """
    A callable wrapper that manages different versions of a function.
    """
    def __init__(self, func_key):
        """
        Initialize the VersionedFunction.

        Args:
            func_key (str): The unique key of the function being versioned.
        """
        self.name = func_key
        self.versions = _version_registry[func_key]

    def __call__(self, *args, version=None, **kwargs):
        """
        Call the specified version of the function.

        Args:
            version (str, optional): The version to execute. Defaults to the latest version.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the function call.

        Raises:
            VersionNotFoundError: If the specified version does not exist.
            ValueError: If no versions are registered.
        """
        if not self.versions:
            raise ValueError(f"No versions registered for function '{self.name}'.")

        if version is not None:
            if version in self.versions:
                func = self.versions[version]
                if getattr(func, '_deprecated', False):
                    warnings.warn(
                        f"Version '{version}' of function '{self.name}' is deprecated.",
                        DeprecationWarning
                    )
                return func(*args, **kwargs)
            else:
                raise VersionNotFoundError(
                    f"Version '{version}' not found for function '{self.name}'."
                )
        else:
            # Default to the latest version based on semantic versioning
            latest_version = self._get_latest_version()

            return self.versions[latest_version](*args, **kwargs)

    def __get__(self, instance, owner):
        """
        Descriptor method to support instance methods and inheritance.
        """
        # Merge versions from base classes
        merged_versions = self._get_versions_in_mro(owner)
        self.versions = merged_versions

        if instance is None:
            # Accessed via class, return self
            return self
        else:
            # Return a bound method
            return MethodType(self, instance)

    def add_version(self, version_id, func):
        """
        Add a new version to the function.

        Args:
            version_id (str): The version identifier (e.g., "1.0.0").
            func (callable): The function implementation.

        Raises:
            ValueError: If the version_id is already registered.
            ValueError: If the version_id is not a valid semantic version.
        """
        if version_id in self.versions:
            raise ValueError(
                f"Version '{version_id}' is already registered for function '{self.name}'."
            )
        # Validate semantic versioning
        try:
            pkg_version.parse(version_id)
        except pkg_version.InvalidVersion:
            raise ValueError(
                f"Version '{version_id}' is not a valid semantic version."
            )
        self.versions[version_id] = func

    def available_versions(self):
        """
        Return a list of available version IDs, sorted in ascending order.

        Returns:
            list: List of version identifiers.
        """
        return sorted(self.versions.keys(), key=lambda v: pkg_version.parse(v))

    def deprecate_version(self, version_id):
        """
        Deprecate a specific version of the function.

        Args:
            version_id (str): The version identifier to deprecate.

        Raises:
            VersionNotFoundError: If the specified version does not exist.
        """
        if version_id in self.versions:
            setattr(self.versions[version_id], '_deprecated', True)
        else:
            raise VersionNotFoundError(
                f"Version '{version_id}' not found for function '{self.name}'."
            )

    def remove_version(self, version_id):
        """
        Remove a specific version of the function.

        Args:
            version_id (str): The version identifier to remove.

        Raises:
            VersionNotFoundError: If the specified version does not exist.
        """
        if version_id in self.versions:
            del self.versions[version_id]
        else:
            raise VersionNotFoundError(
                f"Version '{version_id}' not found for function '{self.name}'."
            )

    def _get_latest_version(self):
        """
        Determine the latest version based on semantic versioning.

        Returns:
            str: The latest version identifier.
        """
        if not self.versions:
            raise ValueError(f"No versions registered for function '{self.name}'.")

        # Sort versions using semantic versioning
        sorted_versions = sorted(
            self.versions.keys(),
            key=lambda v: pkg_version.parse(v),
            reverse=True
        )
        return sorted_versions[0]

    def _get_versions_in_mro(self, owner):
        """ Get versions from the method resolution order (MRO) for inheritance. """
        versions = {}
        attr_name = self.name.split('.')[-1]
        for cls in owner.mro():
            cls_attr = cls.__dict__.get(attr_name)
            if isinstance(cls_attr, VersionedFunction):
                versions.update(cls_attr.versions)
            elif isinstance(cls_attr, (classmethod, staticmethod)) and isinstance(cls_attr.__func__, VersionedFunction):
                versions.update(cls_attr.__func__.versions)
        return versions

    @property
    def versions_dict(self):
        """
        Access the versions dictionary directly.

        Returns:
            dict: The versions dictionary.
        """
        return self.versions


def version(version_id):
    """ Decorator to register a function version. """
    def decorator(func):
        original_func = func
        is_classmethod = False
        is_staticmethod = False

        # Unwrap if it's a classmethod or staticmethod
        if isinstance(func, classmethod):
            is_classmethod = True
            original_func = func.__func__
        elif isinstance(func, staticmethod):
            is_staticmethod = True
            original_func = func.__func__

        func_key = f"{original_func.__module__}.{original_func.__qualname__}"

        # Validate semantic versioning using packaging.version
        try:
            Version(version_id)
        except InvalidVersion:
            raise ValueError(f"Version '{version_id}' is not a valid semantic version.")

        # Check if the function is already versioned with the same version
        if version_id in _version_registry.get(func_key, {}):
            raise ValueError(
                f"Version '{version_id}' is already registered for function '{func_key}'."
            )

        # Register the function version
        _version_registry[func_key][version_id] = original_func

        # Create the VersionedFunction wrapper
        wrapper = VersionedFunction(func_key)

        # Re-apply classmethod or staticmethod if necessary
        if is_classmethod:
            return classmethod(wrapper)
        elif is_staticmethod:
            return staticmethod(wrapper)
        else:
            return wrapper

    return decorator