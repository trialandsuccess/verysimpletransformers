"""
Core functionality of this library.
"""
import struct
import sys
import typing
import warnings
import zlib
from pathlib import Path

import dill  # nosec
import torch
from tqdm import tqdm

from .metadata import (
    as_version,
    compare_versions,
    get_metadata,
    get_simpletransformers_version,
    get_transformers_version,
    get_verysimpletransformers_version,
)
from .metadata_schema import MetaHeader
from .support import CudaUnpickler, TqdmProgress, as_binaryio, dummy_tqdm, write_bundle
from .versioning import get_version

if typing.TYPE_CHECKING:  # pragma: no cover
    from .types import AllSimpletransformersModels

from configuraptor import asbytes


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
    print("Starting dump...", file=sys.stderr)

    with tqdm(total=100) as progress:
        progress.update(10)
        pickled = dill.dumps(model)
        progress.update(40)
        pickled = zlib.compress(pickled, level=int(compression))  # compression of 0 still slightly changes the bytes!
        progress.update(30)

        output_file = as_binaryio(output_file, "wb")

        hashbang = b"#!/usr/bin/env verysimpletransformers\n"
        metadata = asbytes(get_metadata(len(pickled), compression_level=compression, device=model.device))
        progress.update(10)

        write_bundle(output_file, hashbang, metadata, pickled)
        progress.update(10)

    print("Finished dump, wrote file!", file=sys.stderr)
    return output_file


bundle_model = to_vst


def load_compressed_model(
    compressed: bytes, device: str, progress: TqdmProgress = dummy_tqdm
) -> "AllSimpletransformersModels":
    """
    Load compressed bytes into an actual simple transformers model, move cuda settings around.
    """
    compressed = zlib.decompress(compressed)
    progress.update(30)

    # load + fix cuda (pt1):
    result: "AllSimpletransformersModels" = CudaUnpickler.loads(compressed, device=device)
    # fix cuda (pt2):
    result.device = device

    progress.update(20)
    return result


def _run_metadata_checks(data: bytes, cls: typing.Type[MetaHeader]) -> None:
    metadata: MetaHeader = cls.load(data)
    # metadata is versioned, so properties can change. Use 'getattr' to prevent issues!

    compare_versions("transformers", getattr(metadata, "transformers_version", None), get_transformers_version())

    compare_versions(
        "simple transformers", getattr(metadata, "simpletransformers_version", None), get_simpletransformers_version()
    )

    compare_versions(
        "very simple transformers",
        getattr(metadata, "verysimpletransformers_version", None),
        get_verysimpletransformers_version(),
    )

    if torch_version := getattr(metadata, "torch_version", None):
        compare_versions("torch", as_version(torch_version), as_version(torch.__version__))


def run_metadata_checks(
    open_file: typing.BinaryIO, meta_length: int, version: int | typing.Literal["latest"] = "latest"
) -> None:
    """
    Given an open file object, the meta length and version, try to parse the Meta Header object and run some \
        check on it.

    If this fails, no worries but warn the user about it.
    """
    if cls := get_version(MetaHeader, version):
        try:
            return _run_metadata_checks(open_file.read(meta_length), cls)
        except Exception as e:
            warnings.warn(
                "An issue occurred while attempting to extract the file's metadata. "
                "We will proceed with loading your model, but this may result in potential problems.",
                category=BytesWarning,
                source=e,
            )


def _from_vst(open_file: typing.BinaryIO, device: str = "auto") -> "AllSimpletransformersModels":
    # todo: currently, cuda is always converted to CPU.
    #   this should be 1. selectable by the user and/or 2. some based on cuda.is_available().
    #   cuda info should also be stored in the metadata (available + enabled)
    with tqdm(total=100) as progress:
        progress.update(10)
        next(open_file)  # skip first line (hashbang)

        # extract lengths before actually loading meta header object,
        # because its variable!
        version, meta_length, content_length = struct.unpack("H H Q", open_file.read(16))

        run_metadata_checks(open_file, meta_length, version)

        # todo: device from metadata + args
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"{device=}")
        progress.update(20)

        pickled = open_file.read(content_length)
        progress.update(20)

        return load_compressed_model(pickled, device, progress)


def from_vst(input_file: str | Path | typing.BinaryIO, device: str = "auto") -> "AllSimpletransformersModels":
    """
    Given a file path-like object, load the Simple Transformers model back into memory.
    """
    print("Starting load", file=sys.stderr)

    with as_binaryio(input_file) as f:
        result = _from_vst(f, device=device)

    print("Finished load!", file=sys.stderr)
    return result


load_model = from_vst
