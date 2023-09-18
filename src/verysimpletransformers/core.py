import struct
import typing
import zlib
from io import BytesIO
from pathlib import Path

import dill

from .metadata import Metadata, MetaHeader, get_metadata
from .metadata_schema import get_version

if typing.TYPE_CHECKING:
    from .types import AllSimpletransformersModels


def write_bundle(output_file: typing.BinaryIO, *to_write: bytes) -> None:
    with output_file as f_out:
        for element in to_write:
            f_out.write(element)


def as_binaryio(file: str | Path | typing.BinaryIO | None, mode: typing.Literal["rb", "wb"] = "rb") -> typing.BinaryIO:
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
    pickled = dill.dumps(model)
    pickled = zlib.compress(pickled, level=int(compression))  # compression of 0 still slightly changes the bytes!

    output_file = as_binaryio(output_file, "wb")

    hashbang = b"#!/usr/bin/env verysimpletransformers\n"
    metadata = get_metadata(len(pickled), compression_level=compression)._pack()

    write_bundle(output_file, hashbang, metadata, pickled)

    return output_file


bundle = to_vst


def from_vst(input_file: str | Path | typing.BinaryIO) -> "AllSimpletransformersModels":
    # todo: deal with cuda *maybe* available
    input_file = as_binaryio(input_file)

    with input_file as f:
        next(f)  # skip first line

        # extract lengths before actually loading meta header object,
        # because its variable!
        version, meta_length, content_length = struct.unpack("H H Q", f.read(16))
        metadata = get_version(MetaHeader, version).load(f.read(meta_length))
        # todo: metadata checks

        pickled = f.read(content_length)

    pickled = zlib.decompress(pickled)
    return dill.loads(pickled)


load_model = from_vst
