"""
Core functionality of this library.
"""
import io
import struct
import sys
import typing
import zlib
from io import BytesIO
from pathlib import Path

import dill  # nosec
import torch
from dill import Unpickler  # nosec
from tqdm import tqdm

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
    print("Starting dump...", file=sys.stderr)

    with tqdm(total=100) as progress:
        progress.update(10)
        pickled = dill.dumps(model)
        progress.update(40)
        pickled = zlib.compress(pickled, level=int(compression))  # compression of 0 still slightly changes the bytes!
        progress.update(30)

        output_file = as_binaryio(output_file, "wb")

        hashbang = b"#!/usr/bin/env verysimpletransformers\n"
        metadata = get_metadata(len(pickled), compression_level=compression)._pack()
        progress.update(10)

        write_bundle(output_file, hashbang, metadata, pickled)
        progress.update(10)

    print("Finished dump, wrote file!", file=sys.stderr)
    return output_file


bundle = to_vst


class CudaUnpickler(Unpickler):  # type: ignore
    """
    Custom unpickler that deals with cuda being possibly available or missing.
    """

    def __init__(self, filelike: typing.BinaryIO, *a: typing.Any, device: str = "cpu", **kw: typing.Any):
        """
        You can choose a device to load the model onto (cpu, cuda).
        """
        self.device = device
        super().__init__(filelike, *a, **kw)

    def find_class(self, module: str, name: str) -> typing.Any:
        """
        Custom unpickling behavior.
        """
        if module == "torch.storage" and name == "_load_from_bytes":
            return lambda b: torch.load(io.BytesIO(b), map_location=self.device)
        else:
            return super().find_class(module, name)

    @classmethod
    def loads(cls, data: bytes, device: str = "cpu") -> typing.Any:
        """
        Shortcut for creating an instance and calling .load on it.
        """
        return cls(io.BytesIO(data), device=device).load()


class DummyTqdm:
    """
    Can be used in stead of a tqdm object but this does nothing.
    """

    def update(self, _: int) -> bool | None:
        """
        Same signature as tqdm.update.
        """
        return None


dummy_tqdm = DummyTqdm()


class TqdmProgress(typing.Protocol):
    """
    Protocol for tqdm, so DummyTqdm can be passed as well.
    """

    def update(self, num: int) -> bool | None:
        """
        The signature of tqdm.update.
        """


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
        if cls := get_version(MetaHeader, version):
            metadata = cls.load(open_file.read(meta_length))  # type: ignore
        # else: ...
        # todo: metadata checks
        # todo: device from metadata + args
        print(metadata)
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
