# funcversion/__init__.py

from .core import VersionedFunction
from .version import version
from .exceptions import VersionNotFoundError

__all__ = ['VersionedFunction', 'VersionNotFoundError', 'version']
