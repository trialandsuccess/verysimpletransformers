"""
Functions to deal with metadata of `.vst` files.
"""

import re
import sys

import transformers
from plumbum import local
from plumbum.cmd import grep

from .metadata_schema import Metadata, MetaHeader, Version


def as_version(version_str: str) -> Version:
    """
    Convert a version string into a binary Version object.
    """
    version = Version()
    version.major, version.minor, version.patch = (int(_) for _ in version_str.split("."))

    return version


def _simpletransformers_version() -> str:
    """
    Get the installed ST version.
    """
    _python = sys.executable
    python = local["python"]
    options = (python["-m", "pip", "freeze"] | grep["simpletransformers"])()

    return next(re.finditer(r"simpletransformers==(\d+\.\d+\.\d+)", options)).group(1)


def get_simpletransformers_version() -> Version:
    """
    Get the installed simple transformers version as a binary Version object.
    """
    return as_version(_simpletransformers_version())


def _transformers_version() -> str:
    """
    Get the installed transformers version.
    """
    return str(transformers.__version__)


def get_transformers_version() -> Version:
    """
    Get the installed transformers version as a binary Version object.
    """
    return as_version(_transformers_version())


def get_metadata(content_length: int, compression_level: int) -> Metadata:
    """
    Build the binary metadata object that is prefixed before the model data.

    `header` can be versioned and thus changed, the top-level metadata object can not be changed,
    due to backwards compatibility. This layer contains the lengths of each section of the .vst file,
    and the loader expects these to be correct. If the metadata itself can not be parsed, we can still load the
    actual ML model and just show a warning about the metadata.
    """
    header = MetaHeader()

    header.welcome_text = (
        "--- Welcome to Very Simple Transformers! ---\n"
        + "Installation: `pip install verysimpletransformers`\n"
        + "Usage: `python -m verysimpletransformers model.vst`\n"
    )

    header.simple_transformers_version = get_simpletransformers_version()
    header.transformers_version = get_transformers_version()
    header.compression_level = compression_level

    meta = Metadata()

    meta.meta_version = 1
    meta.meta_length = header._get_length()
    meta.content_length = content_length
    meta.meta_header = header

    return meta
