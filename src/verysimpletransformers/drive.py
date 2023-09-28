"""
Simple Google Drive API to store models (.vst files).

NOTE: This does not really use pytest, since it is very hard to test with the Google Drive API..
"""
from __future__ import annotations

import io
import typing
import warnings
from pathlib import Path

try:
    from drive_in import DriveSingleton
    from drive_in.helpers import extract_google_id
except ImportError as e:
    warnings.warn(
        "drive extension not installed. from_drive and to_drive functionality will not be available.",
        category=ImportWarning,
        source=e,
    )

from . import from_vst, to_vst
from .types import SimpleTransformerProtocol


def to_drive(
    file_path: str | Path | typing.BinaryIO | SimpleTransformerProtocol,
    filename: str = None,
    folder: str = None,
    chunks_size_mb: int = 25,
) -> str:  # pragma: no cover
    """
    Simplified API to upload a (vst) file to Drive.
    """
    drive = DriveSingleton()  # will authenticate only on creation of first instance.

    file_obj: str | Path | typing.BinaryIO
    if isinstance(file_path, SimpleTransformerProtocol):
        file_obj = io.BytesIO()
        to_vst(file_path, file_obj)
        filename = filename or f"{file_path.__class__.__name__}.vst"
    else:
        file_obj = file_path

    return drive.upload(file_obj, filename, folder, chunks_size_mb)


def from_drive(url_or_id: str) -> SimpleTransformerProtocol:
    drive = DriveSingleton()

    file_id = extract_google_id(url_or_id)

    data = drive.download(file_id)

    return from_vst(data)


def main() -> list[str]:
    # model = DummyModel()
    #
    # return to_drive(model)

    model = from_drive("https://drive.google.com/file/d/1r1ETM7GyRwyGw1ziPmymkEtL--Hx2ZwP/view?usp=drive_link")

    result, _ = model.predict(["Hello there"])
    print(result)
    return typing.cast(list[str], result)
