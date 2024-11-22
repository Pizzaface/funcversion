# funcversion/core.py

import warnings
from collections import defaultdict
from types import MethodType
from typing import Any, Callable, Type, Optional, Union

from packaging import version as pkg_version  # For semantic versioning

from .exceptions import VersionNotFoundError

# Global registry to store function versions
_version_registry: defaultdict[str, dict[str, Callable]] = defaultdict(dict)

# Registry to store VersionedFunction instances
_versioned_functions_registry: dict[str, 'VersionedFunction'] = {}


class VersionedFunction:
    """
    A callable wrapper that manages different versions of a function.
    """

    def __init__(self, func_key: str) -> None:
        """
        Initialize the VersionedFunction.

        Args:
            func_key (str): The unique key of the function being versioned.
        """
        self.name: str = func_key
        self.versions: dict[str, Callable] = _version_registry[func_key]

    def __call__(self, *args: Any, version: str | None = None, **kwargs: Any) -> Any:
        """
        Call the specified version of the function.

        Args:
            version (str, optional): The version to execute. Defaults to the latest version.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function call.

        Raises:
            VersionNotFoundError: If the specified version does not exist.
            ValueError: If no versions are registered and no version is specified.
        """
        if version is not None:
            return self._call_specific_version(version, *args, **kwargs)
        else:
            return self._call_latest_version(*args, **kwargs)

    def __get__(self, instance: Optional[Any], owner: Type[Any]) -> Union['VersionedFunction', MethodType]:
        """
        Descriptor method to support instance methods and inheritance.

        Args:
            instance (Any, optional): The instance accessing the method.
            owner (Type[Any]): The owner class.

        Returns:
            Union[VersionedFunction, MethodType]: The bound method or self.
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

    def add_version(self, version_id: str, func: Callable) -> None:
        """
        Add a new version to the function.

        Args:
            version_id (str): The version identifier (e.g., "1.0.0").
            func (Callable): The function implementation.

        Raises:
            ValueError: If the version_id is already registered.
            ValueError: If the version_id is not a valid semantic version.
        """
        self._validate_new_version(version_id)
        self.versions[version_id] = func

    @property
    def available_versions(self) -> list[str]:
        """
        Return a list of available version IDs, sorted in ascending order.

        Returns:
            list[str]: list of version identifiers.
        """
        return sorted(self.versions.keys(), key=lambda v: pkg_version.parse(v))

    @property
    def deprecated_versions(self) -> list[str]:
        """
        Return a list of deprecated version IDs.

        Returns:
            list[str]: list of deprecated version identifiers.
        """
        return [version for version, func in self.versions.items() if getattr(func, '_deprecated', False)]

    @property
    def callables(self) -> dict[str, Callable]:
        """
        list all callable implementations with their version IDs.

        Returns:
            dict[str, Callable]: Mapping of version IDs to callables.
        """
        return dict(self.versions)

    @property
    def current_version(self) -> str:
        """
        Return the current version of the function.

        Returns:
            str: The current version identifier.
        """
        return self._get_latest_version()

    def deprecate_version(self, version_id: str) -> None:
        """
        Deprecate a specific version of the function.

        Args:
            version_id (str): The version identifier to deprecate.

        Raises:
            VersionNotFoundError: If the specified version does not exist.
        """
        if self._version_exists(version_id):
            self.versions[version_id]._deprecated = True
        else:
            raise VersionNotFoundError(f"Version '{version_id}' not found for function '{self.name}'.")

    def remove_version(self, version_id: str) -> None:
        """
        Remove a specific version of the function.

        Args:
            version_id (str): The version identifier to remove.

        Raises:
            VersionNotFoundError: If the specified version does not exist.
        """
        if self._version_exists(version_id):
            del self.versions[version_id]
        else:
            raise VersionNotFoundError(f"Version '{version_id}' not found for function '{self.name}'.")

    def _get_latest_version(self) -> str:
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
            reverse=True,
        )
        return sorted_versions[0]

    def _get_versions_in_mro(self, owner: Type[Any]) -> dict[str, Callable]:
        """
        Get versions from the method resolution order (MRO) for inheritance.

        Args:
            owner (Type[Any]): The owner class.

        Returns:
            dict[str, Callable]: Merged versions from the MRO.
        """
        versions: dict[str, Callable] = {}
        attr_name = self.name.split('.')[-1]
        for cls in owner.mro():
            cls_attr = cls.__dict__.get(attr_name)
            if isinstance(cls_attr, VersionedFunction):
                versions.update(cls_attr.versions)
            elif isinstance(cls_attr, (classmethod, staticmethod)) and isinstance(cls_attr.__func__, VersionedFunction):
                versions.update(cls_attr.__func__.versions)
        return versions

    @property
    def versions_dict(self) -> dict[str, Callable]:
        """
        Access the versions dictionary directly.

        Returns:
            dict[str, Callable]: The versions' dictionary.
        """
        return self.versions

    def __repr__(self) -> str:
        """
        Return a string representation of the VersionedFunction.

        Returns:
            str: The string representation.
        """
        return f'<VersionedFunction {self.name} versions: {self.available_versions}>'

    # Helper Methods to Reduce Conditional Complexity

    def _call_specific_version(self, version: str, *args: Any, **kwargs: Any) -> Any:
        """
        Call a specific version of the function.

        Args:
            version (str): The version to call.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Result of the function call.

        Raises:
            VersionNotFoundError: If the version does not exist.
        """
        if self._version_exists(version):
            func = self.versions[version]
            self._warn_if_deprecated(func, version)
            return func(*args, **kwargs)
        else:
            raise VersionNotFoundError(f"Version '{version}' not found for function '{self.name}'.")

    def _call_latest_version(self, *args: Any, **kwargs: Any) -> Any:
        """
        Call the latest version of the function.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Result of the function call.

        Raises:
            ValueError: If no versions are registered.
        """
        if not self.versions:
            raise ValueError(f"No versions registered for function '{self.name}'.")
        latest_version = self._get_latest_version()
        func = self.versions[latest_version]
        self._warn_if_deprecated(func, latest_version)
        return func(*args, **kwargs)

    def _warn_if_deprecated(self, func: Callable, version: str) -> None:
        """
        Issue a deprecation warning if the function version is deprecated.

        Args:
            func (Callable): The function to check.
            version (str): The version identifier.
        """
        if getattr(func, '_deprecated', False):
            warnings.warn(
                f"Version '{version}' of function '{self.name}' is deprecated.",
                DeprecationWarning,
            )

    def _validate_new_version(self, version_id: str) -> None:
        """
        Validate that the new version can be added.

        Args:
            version_id (str): The version identifier to validate.

        Raises:
            ValueError: If the version is already registered or invalid.
        """
        if self._version_exists(version_id):
            raise ValueError(f"Version '{version_id}' is already registered for function '{self.name}'.")
        if not self._is_valid_semantic_version(version_id):
            raise ValueError(f"Version '{version_id}' is not a valid semantic version.")

    def _version_exists(self, version_id: str) -> bool:
        """
        Check if a version exists.

        Args:
            version_id (str): The version identifier to check.

        Returns:
            bool: True if exists, False otherwise.
        """
        return version_id in self.versions

    @staticmethod
    def _is_valid_semantic_version(version_id: str) -> bool:
        """
        Validate semantic versioning.

        Args:
            version_id (str): The version identifier to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            pkg_version.parse(version_id)
            return True
        except pkg_version.InvalidVersion:
            return False
