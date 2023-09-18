import typing
import warnings
from collections import defaultdict

from configuraptor import BinaryConfig, BinaryField

VERSIONS = defaultdict(dict)

T = typing.TypeVar("T")


def define_version(version_no: int) -> typing.Callable[[T], T]:
    def wraps(cls):
        VERSIONS[cls.__name__][version_no] = cls
        cls.__version__ = version_no
        return cls

    return wraps


def _get_version(cls: T, version="latest") -> T:
    versions = VERSIONS[cls.__name__]
    return max(versions) if version == "latest" else versions[version]


def get_version(cls: T, version: int | typing.Literal["latest"] = "latest") -> T | None:
    try:
        return _get_version(cls, version)
    except Exception as e:
        if version != "latest":
            warnings.warn(f"Specific version {version} not available! Using latest.", source=e)
            return _get_version(cls, "latest")


class Version(BinaryConfig):
    major = BinaryField(int, format="H")
    minor = BinaryField(int, format="H")
    patch = BinaryField(int, format="H")

    def __str__(self):
        return f"Version<{self.major}.{self.minor}.{self.patch}>"


@define_version(0)
class MetaHeader(BinaryConfig):
    welcome_text = BinaryField(str, length=16)


@define_version(1)
class MetaHeader(BinaryConfig):
    welcome_text = BinaryField(str, length=256)
    simple_transformers_version = BinaryField(Version)
    transformers_version = BinaryField(Version)
    compression_level = BinaryField(int, format="H")

    def __repr__(self) -> str:
        result = "MetaHeader<"
        for name, field in self._fields.items():
            value = getattr(self, name)
            result += f"{name}={value}, "
        return f"{result[:-2]}>"


class Metadata(BinaryConfig):
    # don't touch this!
    # MetaHeader can be versioned but for backwards compatiblity we assume this stays the same!
    meta_version = BinaryField(int, format="H")
    meta_length = BinaryField(int, format="H")
    content_length = BinaryField(int, format="Q")
    meta_header = BinaryField(MetaHeader)
