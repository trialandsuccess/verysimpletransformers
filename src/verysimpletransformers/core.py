"""
Core functionality of this library.
"""
from __future__ import annotations

import struct
import sys
import typing
import warnings
import zlib
from pathlib import Path
from pickle import UnpicklingError  # nosec

import dill  # nosec
import torch
from configuraptor import asbytes
from tqdm import tqdm

from .exceptions import BaseVSTException, CorruptedModelException
from .metadata import (
    as_version,
    compare_versions,
    get_metadata,
    get_simpletransformers_version,
    get_transformers_version,
    get_verysimpletransformers_version,
)
from .metadata_schema import Metadata, MetaHeader
from .support import (
    CudaUnpickler,
    DummyTqdm,
    RedirectStdStreams,
    TqdmProgress,
    as_binaryio,
    devnull,
    dummy_tqdm,
    write_bundle,
)
from .types import SimpleTransformerProtocol
from .versioning import get_version

if typing.TYPE_CHECKING:  # pragma: no cover
    from .types import AllSimpletransformersModels

ZeroThroughNine = typing.Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def to_vst(
    model: "AllSimpletransformersModels",
    output_file: str | Path | typing.BinaryIO | None,
    compression: bool | ZeroThroughNine = False,
) -> typing.BinaryIO:
    """
    Convert a trained Simple Transformers model into a .vst file.

    If output_file is None, it is returned as a BytesIO instead.

    Also known as 'bundle'
    """
    if not model:
        raise ValueError("No model provided!")

    print("Starting dump...", file=sys.stderr)

    with tqdm(total=100) as progress:
        progress.update(10)
        pickled = dill.dumps(model)
        progress.update(40)
        if not isinstance(compression, int):
            # weird, but just set to disable.
            compression = 0

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
    try:
        compressed = zlib.decompress(compressed)
    except zlib.error as e:
        raise CorruptedModelException("compression", e) from e

    progress.update(30)

    # load + fix cuda (pt1):
    try:
        result: "AllSimpletransformersModels" = CudaUnpickler.loads(compressed, device=device)
    except UnpicklingError as e:
        raise CorruptedModelException("pickling", e) from e

    # fix cuda (pt2):
    result.device = device

    progress.update(20)
    return result


def _run_metadata_checks(data: bytes, cls: typing.Type[MetaHeader]) -> tuple[bool, MetaHeader]:
    metadata: MetaHeader = cls.load(data)
    # metadata is versioned, so properties can change. Use 'getattr' to prevent issues!
    results: set[bool] = {
        compare_versions(
            "transformers",
            getattr(metadata, "transformers_version", None),
            get_transformers_version(),
        ),
        compare_versions(
            "simple transformers",
            getattr(metadata, "simpletransformers_version", None),
            get_simpletransformers_version(),
        ),
        compare_versions(
            "very simple transformers",
            getattr(metadata, "verysimpletransformers_version", None),
            get_verysimpletransformers_version(),
        ),
    }

    if torch_version := getattr(metadata, "torch_version", None):
        results.add(compare_versions("torch", as_version(torch_version), as_version(torch.__version__)))

    return all(results), metadata


def run_metadata_checks(
    open_file: typing.BinaryIO, meta_length: int, version: int | typing.Literal["latest"] = "latest"
) -> tuple[bool, MetaHeader | None]:
    """
    Given an open file object, the meta length and version, try to parse the Meta Header object and run some \
        check on it.

    If this fails, no worries but warn the user about it.
    """
    latest_version = get_version(MetaHeader, "latest")
    if cls := get_version(MetaHeader, version):
        try:
            checks_pass, metadata = _run_metadata_checks(open_file.read(meta_length), cls)
            if not checks_pass:
                warnings.warn(
                    "Not all metadata checks passed! "
                    "We will proceed with loading your model, but this may result in potential problems. "
                    "This warning can be fixed by updating your model: `verysimpletransformers upgrade model.vst`"
                )

            if not (is_latest := (version == "latest" or getattr(latest_version, "__version__") == version)):
                warnings.warn(
                    "Model has an outdated metadata section! "
                    "We will proceed with loading your model, but this may result in potential problems. "
                    "This warning can be fixed by updating your model: `verysimpletransformers upgrade model.vst`"
                )

            return checks_pass and is_latest, metadata

        except Exception as e:
            warnings.warn(
                "An issue occurred while attempting to extract the file's metadata. "
                "We will proceed with loading your model, but this may result in potential problems.",
                category=BytesWarning,
                source=e,
            )

    return False, None


if typing.TYPE_CHECKING:  # pragma: no cover

    @typing.overload
    def _from_vst(  # type: ignore
        open_file: typing.BinaryIO,
        with_metadata: typing.Literal[True] = True,
        with_model: typing.Literal[True] = True,
        with_progress: bool = True,
        device: str = "auto",
    ) -> tuple["AllSimpletransformersModels", Metadata, bool]:
        ...

    @typing.overload
    def _from_vst(  # type: ignore
        open_file: typing.BinaryIO,
        with_metadata: typing.Literal[False] = False,
        with_model: typing.Literal[True] = True,
        with_progress: bool = True,
        device: str = "auto",
    ) -> tuple["AllSimpletransformersModels", None, bool]:
        ...

    @typing.overload
    def _from_vst(  # type: ignore
        open_file: typing.BinaryIO,
        with_metadata: typing.Literal[True] = True,
        with_model: typing.Literal[False] = False,
        with_progress: bool = True,
        device: str = "auto",
    ) -> tuple[None, Metadata, bool]:
        ...

    @typing.overload
    def _from_vst(
        open_file: typing.BinaryIO,
        with_metadata: typing.Literal[False] = False,
        with_model: typing.Literal[False] = False,
        with_progress: bool = True,
        device: str = "auto",
    ) -> tuple[None, None, bool]:
        ...


def _from_vst(
    open_file: typing.BinaryIO,
    with_metadata: bool = False,
    with_model: bool = True,
    with_progress: bool = True,
    device: str = "auto",
) -> tuple[typing.Optional["AllSimpletransformersModels"], typing.Optional[Metadata], bool]:
    """
    Load the model from a (possibly compressed) dill.

    Checks metadata and optionally returns it as well.
    with_model can be set to False with with_metadata=True to only return the metadata.

    Device (cpu, cuda) will be chosen based on availability if device is set to 'auto'.

    By default, a progress bar will be shown. Use with_progress = False to disable this.
    """
    _progress = tqdm(total=100) if with_progress else DummyTqdm()

    try:
        with _progress as progress:
            progress.update(10)
            next(open_file)  # skip first line (hashbang)

            # extract lengths before actually loading meta header object,
            # because its variable!
            version, meta_length, content_length = struct.unpack("H H Q", open_file.read(16))

            meta_check_passed, meta_header = run_metadata_checks(open_file, meta_length, version)

            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"

            progress.update(20)

            if with_model:
                pickled = open_file.read(content_length)
                progress.update(20)
                model = load_compressed_model(pickled, device, progress)
            else:
                model = None
                progress.update(70)  # 20 from pickling + 50 from `load_compressed_model`

        if with_metadata:
            metadata = Metadata()
            metadata.meta_version = version
            metadata.meta_length = meta_length
            metadata.content_length = content_length
            metadata.meta_header = meta_header or MetaHeader()  # todo: will empty header be enough as fallback?
        else:
            metadata = None

        if with_model:
            print(f"{device=}", file=sys.stderr)
        return model, metadata, meta_check_passed
    except BaseVSTException:
        # don't catch our own exceptions!
        raise
    except Exception as e:  # pragma: no cover
        raise CorruptedModelException("unknown", e) from e


def from_vst(input_file: str | Path | typing.BinaryIO, device: str = "auto") -> "AllSimpletransformersModels":
    """
    Given a file path-like object, load the Simple Transformers model back into memory.
    """
    print("Starting load", file=sys.stderr)

    with as_binaryio(input_file) as f:
        result, _, _ = _from_vst(f, device=device)

    print("Finished load!", file=sys.stderr)
    return result


def from_vst_with_metadata(
    input_file: str | Path | typing.BinaryIO, device: str = "auto"
) -> tuple["AllSimpletransformersModels", Metadata, bool]:
    """
    Given a file path-like object, load the Simple Transformers model back into memory.

    Also validate metadata and return it with the model
    """
    print("Starting load", file=sys.stderr)

    with as_binaryio(input_file) as f:
        result = _from_vst(f, device=device, with_metadata=True)

    print("Finished load!", file=sys.stderr)
    return result


def upgrade_metadata(
    input_file: str | Path | typing.BinaryIO,
    output_file: str | Path | typing.BinaryIO,
    compression: int = 0,
) -> bool:
    """
    Set the input_file's metadata to the latest version (on this system) and save it in output_file.

    Returns a bool that indicates whether an update was executed.
    """
    with as_binaryio(input_file) as f, RedirectStdStreams(stdout=devnull, stderr=devnull):
        model, metadata, valid_meta = _from_vst(f, with_metadata=True, with_model=True, with_progress=False)

    if valid_meta:
        # nothing to do!
        warnings.warn("Model is up-to-date! Not writing to ouput file.")
        return False

    print("Starting upgrade on", input_file, file=sys.stderr)

    compression_level = getattr(metadata.meta_header, "compression_level", 0)
    if not compression and isinstance(compression_level, int):
        compression = compression_level

    compression = min(compression, 9)
    compression = max(compression, 0)
    to_vst(model, output_file, compression=typing.cast(ZeroThroughNine, compression))

    print(f"Completed upgrade on {input_file}. Wrote to {output_file}.", file=sys.stderr)
    return True


load_model = from_vst
load_model_with_metadata = from_vst_with_metadata


def simple_load(filename: str | "AllSimpletransformersModels") -> tuple["AllSimpletransformersModels", str]:
    """
    Helper function for the cli.

    Quietly loads a model (suppress prints to stdout, stderr)
    or just return the model if an existing instance was passed.
    """
    if isinstance(filename, str):
        print("Loading model", filename, "...", file=sys.stderr)
        with RedirectStdStreams(stdout=devnull, stderr=devnull):
            model = from_vst(filename)
        print(f"Done loading {model}!")
    elif isinstance(filename, SimpleTransformerProtocol):
        model = filename
        filename = str(model)
    else:
        raise TypeError(f"Unsupported type {type(filename)}.")

    return model, filename
