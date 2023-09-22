"""
Versioned Metadata classes.
"""

from configuraptor import BinaryConfig, BinaryField

from .versioning import define_version


class Version(BinaryConfig):
    """
    Package version split to binary shorts to save storage.
    """

    major = BinaryField(int, format="H")
    minor = BinaryField(int, format="H")
    patch = BinaryField(int, format="H")

    def __repr__(self) -> str:
        """
        Pretty representation of the version.
        """
        return f"Version<{self.major}.{self.minor}.{self.patch}>"


@define_version(0)
class MetaHeader(BinaryConfig):
    """
    Deprecated.
    """

    welcome_text = BinaryField(str, length=16)


@define_version(1)
class MetaHeader(BinaryConfig):  # type: ignore
    """
    A .vst file has some meta info stored in it.

    Welcome text is simply for users trying to cat/open the file, it contains some simple instructions on how to use it.
    Simple Transformers and Transformers versions are stored, and if the version differs too much from the installed
        version, a warning can be shown. We will still attempt to load the model, since this might still be possible.
    Compression level is stored, but zlib can decompress without it.
    """

    welcome_text = BinaryField(str, length=256)

    transformers_version = BinaryField(Version)
    simpletransformers_version = BinaryField(Version)
    verysimpletransformers_version = BinaryField(Version)

    torch_version = BinaryField(str, length=16)  # includes cpu/cuda so store as str
    cuda_available = BinaryField(bool)
    device = BinaryField(str, length=8)

    compression_level = BinaryField(int, format="H")

    def __repr__(self) -> str:
        """
        Pretty representation of the meta data.
        """
        result = "MetaHeader<"
        for name, field in self._fields.items():
            value = getattr(self, name)
            result += f"{name}={value}, "
        return f"{result[:-2]}>"


class Metadata(BinaryConfig):
    """
    MetaHeader can be versioned but for backwards compatiblity we assume this stays the same!

    !!! don't touch this !!!
    """

    meta_version = BinaryField(int, format="H")
    meta_length = BinaryField(int, format="H")
    content_length = BinaryField(int, format="Q")
    meta_header = BinaryField(MetaHeader)  # todo: can this be typed better? (Versioned class kinda breaks it)
