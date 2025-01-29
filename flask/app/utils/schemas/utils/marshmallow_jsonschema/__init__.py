from pkg_resources import get_distribution

__version__ = "0.1.0"
__license__ = "MIT"

from .base import JSONSchema
from .exceptions import UnsupportedValueError

__all__ = ("JSONSchema", "UnsupportedValueError")
