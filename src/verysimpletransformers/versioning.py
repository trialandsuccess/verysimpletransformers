"""
Logic to create and store multiple versions of a class.
"""

import typing
import warnings
from collections import defaultdict

T = typing.TypeVar("T")


class Versioned(typing.Protocol):
    """
    Protocol for objects that have an internal version attribute.
    """

    __version__: int


class VersionedClass(Versioned, type):
    """
    Protocol to indicate a class with __version__ added.
    """


AnyCls = typing.TypeVar("AnyCls", bound=typing.Type[typing.Any])

VERSIONS: defaultdict[str, dict[int, typing.Type[VersionedClass]]] = defaultdict(dict)


def define_version(version_no: int) -> typing.Callable[[AnyCls], AnyCls]:
    """
    Define a new version of a class using this decorator.

    Example:
        @define_version(1)
        class MyClass: ...
    """

    def wraps(cls: AnyCls) -> AnyCls:
        VERSIONS[cls.__name__][version_no] = cls
        cls.__version__ = version_no
        return cls

    return wraps


def _get_version(cls: AnyCls, version: int | typing.Literal["latest"] = "latest") -> AnyCls:
    versions = VERSIONS[cls.__name__]
    if version == "latest":
        version = max(versions)

    # AnyCls is bound to VersionedClass but mypy doesn't seem to understand that..
    return typing.cast(AnyCls, versions[version])


def get_version(cls: AnyCls, version: int | typing.Literal["latest"] = "latest") -> AnyCls | None:
    """
    Try to get the specific `version` of cls, or return `latest` as a fallback (with a warning).
    """
    try:
        return _get_version(cls, version)
    except Exception as e:
        if version != "latest":
            warnings.warn(f"Specific version {version} not available! Using latest.", source=e)
            return _get_version(cls, "latest")

    return None
