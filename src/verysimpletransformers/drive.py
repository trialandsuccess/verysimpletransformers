"""
Simple Google Drive API to store models (.vst files).

NOTE: This does not really use pytest, since it is very hard to test with the Google Drive API..
"""
from __future__ import annotations

import io
import sys
import typing
from pathlib import Path

from .core import from_vst, to_vst
from .exceptions import ExtraNotInstalledError
from .types import SimpleTransformerProtocol

CLIENT_ID = "327892950221-uaah9475qfsfp64s6nqa3o15a9eh3p67.apps.googleusercontent.com"
REDIRECT_URI = "https://oauth.trialandsuccess.nl/callback"

try:
    from drive_in import DriveSingleton
    from drive_in.helpers import extract_google_id
except ImportError as e:  # pragma: no cover
    raise ExtraNotInstalledError("drive") from e


def to_drive(
    file_path: str | Path | typing.BinaryIO | SimpleTransformerProtocol,
    filename: str = None,
    folder: str = None,
    chunks_size_mb: int = 25,
    # auth:
    client_id: str = None,
    redirect_uri: str = None,
) -> str:
    """
    Simplified API to upload a (vst) file to Drive.

    Args:
        # common:
        file_path:       a running model or path to model file to save to drive
        filename:        the new name on google drive (default will be guessed from file path or model class name)
        folder:          google drive folder id to upload to
        # more rare:
        chunks_size_mb:  customize how many MB should be uploaded for each chunk
        client_id:       optional, for custom oauth
        redirect_uri:    optional, for custom oauth
    """
    drive = DriveSingleton(
        client_id=client_id or CLIENT_ID,
        redirect_uri=redirect_uri or REDIRECT_URI,
    )  # will authenticate only on creation of first instance.

    file_obj: str | Path | typing.BinaryIO
    if isinstance(file_path, SimpleTransformerProtocol):
        file_obj = io.BytesIO()
        to_vst(file_path, file_obj)
        filename = filename or f"{file_path.__class__.__name__}.vst"
    else:
        file_obj = file_path

    return drive.upload(file_obj, filename, folder, chunks_size_mb)


def from_drive(
    url_or_id: str,
    save_to: typing.Optional[str | Path] = None,
    # auth:
    client_id: str = None,
    redirect_uri: str = None,
    cache: bool = True,
) -> SimpleTransformerProtocol:
    """
    Download a model from drive and load it back into memory.

    Args:
        # common:
        url_or_id:    ID or URL to the file (must be created before by `to_drive`)
        save_to:      if the file should also be saved to disk, specify where
        cache:        store the model in a /tmp/vst/... file, so it can easily be reloaded later?
        # more rare
        client_id:    optional, for custom oauth
        redirect_uri: optional, for custom oauth
    """
    drive = DriveSingleton(
        client_id=client_id or CLIENT_ID,
        redirect_uri=redirect_uri or REDIRECT_URI,
    )  # will authenticate only on creation of first instance.

    file_id = extract_google_id(url_or_id)

    if not save_to and cache:
        base = Path("/tmp/vst")
        base.mkdir(exist_ok=True)
        save_to = base / file_id

    if cache and save_to and Path(save_to).exists():
        # don't re-download
        print(
            "File already exists locally, using this version. Use cache=False to prevent this behavior.",
            file=sys.stderr,
        )
        return from_vst(save_to)

    target = save_to or io.BytesIO()
    drive.download(file_id, target)

    return from_vst(target)
