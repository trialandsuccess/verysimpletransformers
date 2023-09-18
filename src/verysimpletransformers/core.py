import struct
import typing
import zlib
from io import BytesIO
from pathlib import Path
import dill

if typing.TYPE_CHECKING:
    from .types import AllSimpletransformersModels


def bundle(
    model: "AllSimpletransformersModels",
    output_file: str | Path | typing.BinaryIO | None,
    compression: bool | typing.Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] = False,
):
    # todo: deal with cuda *maybe* available

    pickled = dill.dumps(model)
    if compression:
        pickled = zlib.compress(pickled, level=compression)

    if isinstance(output_file, str):
        output_file = Path(output_file)
    if isinstance(output_file, Path):
        output_file = output_file.open("wb")
    if output_file is None:
        output_file = BytesIO()

    with output_file as f_out:
        f_out.write(b"#!/usr/bin/python -m verysimpletransformers\n")
        f_out.write(struct.pack("64s", b"# --- Welcome to Very Simple Transformers! ---\n"))
        f_out.write(pickled)

    return output_file
