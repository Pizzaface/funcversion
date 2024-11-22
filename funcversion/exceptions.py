# funcversion/exceptions.py


class VersionNotFoundError(Exception):
    """Exception raised when a specified version is not found."""

    pass


class NoVersionsFoundError(Exception):
    """Exception raised when no versions are found."""

    pass


class InvalidVersionError(Exception):
    """Exception raised when an invalid version is provided."""

    pass


class VersionExistsError(Exception):
    """Exception raised when a version already exists."""

    pass
