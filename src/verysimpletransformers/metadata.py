import re
import struct
import sys

import transformers
from configuraptor import BinaryConfig, BinaryField
from plumbum import local
from plumbum.cmd import grep

from .metadata_schema import Metadata, MetaHeader, Version


def _simpletransformers_version():
    _python = sys.executable
    python = local["python"]
    options = (python["-m", "pip", "freeze"] | grep["simpletransformers"])()

    return next(re.finditer(r"simpletransformers==(\d+\.\d+\.\d+)", options)).group(1)


def as_version(version_str: str) -> Version:
    version = Version()
    version.major, version.minor, version.patch = (int(_) for _ in version_str.split("."))

    return version


def get_simpletransformers_version() -> Version:
    return as_version(_simpletransformers_version())


def _transformers_version():
    return transformers.__version__


def get_transformers_version() -> Version:
    return as_version(_transformers_version())


def get_metadata(content_length: int, compression_level: int) -> Metadata:
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
