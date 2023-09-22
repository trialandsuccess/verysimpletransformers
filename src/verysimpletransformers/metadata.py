"""
Functions to deal with metadata of `.vst` files.
"""

import re
import sys
import warnings

import torch
import transformers
from plumbum import local
from plumbum.cmd import grep

from .__about__ import __version__
from .metadata_schema import Metadata, MetaHeader, Version
from .versioning import get_version


def as_version(version_str: str) -> Version:
    """
    Convert a version string into a binary Version object.
    """
    version = Version()
    version_str = version_str.split("-")[0].split("+")[0]  # remove extra's like `-beta` or `+cpu`.
    version.major, version.minor, version.patch = (int(_) for _ in version_str.split("."))

    return version


def compare_versions(pkg: str, version1: Version | None, version2: Version | None) -> bool:
    """
    Compare two version objects, and warn if the major or minor version differs.
    """
    if not (version1 and version2):
        # check impossible, just skip.
        return False

    if version1.major != version2.major:
        warnings.warn(
            f"!!! DANGER: Installed Major version of {pkg} differs from the one this model was trained on. "
            f"This could lead to compatibility issues!"
        )
        return False
    elif version1.minor != version2.minor:
        warnings.warn(
            f"WARNING: Installed Minor version of {pkg} differs from the one this model was trained on. "
            f"This could potentially lead to compatibility issues!"
        )
        return False

    return True


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


def get_verysimpletransformers_version() -> Version:
    """
    Get the installed very simple transformers version as a binary Version object.
    """
    return as_version(__version__)


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


def get_metadata(content_length: int, compression_level: int, device: str) -> Metadata:
    """
    Build the binary metadata object that is prefixed before the model data.

    `header` can be versioned and thus changed, the top-level metadata object can not be changed,
    due to backwards compatibility. This layer contains the lengths of each section of the .vst file,
    and the loader expects these to be correct. If the metadata itself can not be parsed, we can still load the
    actual ML model and just show a warning about the metadata.
    """
    header_cls = get_version(MetaHeader, "latest")
    if not header_cls:  # pragma: no cover
        raise NotImplementedError("MetaHeader should always have a latest version.")

    header = header_cls()

    header.welcome_text = (
        "--- Welcome to Very Simple Transformers! ---\n"
        + "Installation: `pip install verysimpletransformers`\n"
        + "Usage: `python -m verysimpletransformers model.vst`\n"
    )

    header.transformers_version = get_transformers_version()
    header.simpletransformers_version = get_simpletransformers_version()
    header.verysimpletransformers_version = get_verysimpletransformers_version()

    header.torch_version = torch.__version__
    header.cuda_available = torch.cuda.is_available()
    header.device = device

    header.compression_level = compression_level

    meta = Metadata()

    meta.meta_version = getattr(header_cls, "__version__")
    meta.meta_length = header._get_length()
    meta.content_length = content_length
    meta.meta_header = header

    return meta
