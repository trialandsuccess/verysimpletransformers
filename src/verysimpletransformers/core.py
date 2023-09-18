"""
Core functionality of this library.
"""

import struct
import typing
import zlib
from io import BytesIO
from pathlib import Path

import dill  # nosec

from .metadata import get_metadata
from .metadata_schema import MetaHeader
from .versioning import get_version

if typing.TYPE_CHECKING:  # pragma: no cover
    from .types import AllSimpletransformersModels


def write_bundle(output_file: typing.BinaryIO, *to_write: bytes) -> None:
    """
    Write all extra arguments to the output file.
    """
    with output_file as f_out:
        for element in to_write:
            f_out.write(element)


def as_binaryio(file: str | Path | typing.BinaryIO | None, mode: typing.Literal["rb", "wb"] = "rb") -> typing.BinaryIO:
    """
    Convert a number of possible 'file' descriptions into a single BinaryIO interface.
    """
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        file = file.open(mode)
    if file is None:
        file = BytesIO()

    return file


def to_vst(
    model: "AllSimpletransformersModels",
    output_file: str | Path | typing.BinaryIO | None,
    compression: bool | typing.Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] = False,
) -> typing.BinaryIO:
    """
    Convert a trained Simple Transformers model into a .vst file.

    If output_file is None, it is returned as a BytesIO instead.

    Also known as 'bundle'
    """
    pickled = dill.dumps(model)
    pickled = zlib.compress(pickled, level=int(compression))  # compression of 0 still slightly changes the bytes!

    output_file = as_binaryio(output_file, "wb")

    hashbang = b"#!/usr/bin/env verysimpletransformers\n"
    metadata = get_metadata(len(pickled), compression_level=compression)._pack()

    write_bundle(output_file, hashbang, metadata, pickled)

    return output_file


bundle = to_vst


def from_vst(input_file: str | Path | typing.BinaryIO) -> "AllSimpletransformersModels":
    """
    Given a file path-like object, load the Simple Transformers model back into memory.
    """
    # todo: deal with cuda *maybe* available
    input_file = as_binaryio(input_file)

    with input_file as f:
        next(f)  # skip first line

        # extract lengths before actually loading meta header object,
        # because its variable!
        version, meta_length, content_length = struct.unpack("H H Q", f.read(16))
        if cls := get_version(MetaHeader, version):
            metadata = cls.load(f.read(meta_length))  # type: ignore
        # else: ...
        # todo: metadata checks
        print(metadata)

        pickled = f.read(content_length)

    pickled = zlib.decompress(pickled)
    return dill.loads(pickled)  # nosec


load_model = from_vst
