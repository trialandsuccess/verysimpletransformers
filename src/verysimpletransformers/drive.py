"""
Simple Google Drive API to store models (.vst files).

NOTE: This does not really use pytest, since it is very hard to test with the Google Drive API..
"""

import os
import typing
import uuid
from pathlib import Path

import requests
import tqdm
from configuraptor import Singleton
from yarl import URL

from .exceptions import BaseVSTException

CLIENT_ID = "327892950221-uaah9475qfsfp64s6nqa3o15a9eh3p67.apps.googleusercontent.com"
REDIRECT_URI = "https://oauth.trialandsuccess.nl/callback"
SCOPE = "https://www.googleapis.com/auth/drive.file"


class UploadError(BaseVSTException):
    """
    Raised when something goes wrong while uploading to Drive.
    """


class Drive:  # pragma: no cover
    """
    Simplified class that allows authenticate and uploading (multi part).
    """

    token: str
    base_url = URL("https://www.googleapis.com/upload/drive/v3/")
    auth_url = URL("https://accounts.google.com/o/oauth2/v2/auth")

    def __init__(self, token: str = None, **kw: typing.Any) -> None:
        """
        Provide an existing access_token or be prompted to create one.
        """
        self.token = token or self.authenticate(**kw)

    def generate_headers(self) -> dict[str, str]:
        """
        After .authenticate(), create default auth header.
        """
        return {
            "Authorization": f"Bearer {self.token}",  # Replace with your access token
            "Content-Type": "application/json; charset=UTF-8",
        }

    def authenticate(self, scope: str = SCOPE, redirect_uri: str = REDIRECT_URI, client_id: str = CLIENT_ID) -> str:
        """
        CLI-authenticate: print the URL and prompt for access token.

        Uses oauth.trialandsuccess.nl since a callback URL is required.
         Other methods that do not require a callback, expect a private key or secure config which is not
         feasible for an open source library.
        """
        # Construct the URL
        print(
            self.auth_url
            % {
                "scope": scope,
                "include_granted_scopes": "true",
                "response_type": "token",
                "state": str(uuid.uuid4()),
                "redirect_uri": redirect_uri,
                "client_id": client_id,
            }
        )

        return input("Please paste your token here: ")

    def upload(self, file_path: str | Path, filename: str = None, folder: str = None, chunks_size_mb: int = 25) -> str:
        """
        Upload a file in multiple chunks.

        Returns the new file url.
        """
        if isinstance(file_path, Path):
            file_path = str(file_path.resolve())

        with requests.Session() as session:
            location = self._initialize_upload(file_path, filename, folder, session)

            self._upload_chunks(file_path, location, session, chunks_size_mb)

            metadata = self._finalize_upload(location, session)

        return f"https://drive.google.com/file/d/{metadata['id']}/view"

    def _initialize_upload(
        self, file_path: str, filename: str | None, folder: str | None, session: requests.Session
    ) -> str:
        metadata: dict[str, str | list[str]] = {
            "name": filename or os.path.basename(file_path),
        }
        if folder:
            metadata["parents"] = [folder]
        resp = session.post(
            str(
                self.base_url
                / "files"
                % {
                    "uploadType": "resumable",
                }
            ),
            headers=self.generate_headers(),
            json=metadata,
            timeout=10,
        )
        return resp.headers["Location"]

    def _upload_chunks(self, file_path: str, location: str, session: requests.Session, chunks_size_mb: int) -> None:
        total_size = os.path.getsize(file_path)
        chunk_size = chunks_size_mb * 1024 * 1024  # 50MB chunk size (you can adjust this)
        with tqdm.tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as progress, open(
            file_path, "rb"
        ) as file:
            start_byte = 0
            while start_byte < total_size:
                end_byte = start_byte + chunk_size - 1
                if end_byte >= total_size:
                    end_byte = total_size - 1

                headers = {
                    "Content-Length": str(end_byte - start_byte + 1),
                    "Content-Range": f"bytes {start_byte}-{end_byte}/{total_size}",
                }

                response = session.put(location, headers=headers, data=file.read(chunk_size), timeout=60)

                if response.status_code > 399:
                    raise UploadError(response.text, response.status_code)

                progress.update(end_byte - start_byte + 1)
                start_byte = end_byte + 1

    def _finalize_upload(self, location: str, session: requests.Session) -> dict[str, str]:
        # Step 3: Finalize the upload with a 200 status code
        headers = {"Content-Length": "0"}
        response = session.put(location, headers=headers, timeout=5)
        if response.status_code != 200:
            raise UploadError(response.text, response.status_code)
        metadata = response.json()
        return typing.cast(dict[str, str], metadata)


class DriveSingleton(Drive, Singleton):
    """
    Make sure authentication only happens once, even if trying to create multiple instances.

    (e.g. calling to_drive() multiple times will try to create new Drive objects, but we want to keep the auth info.)
    """


def to_drive(
    file_path: str | Path, filename: str = None, folder: str = None, chunks_size_mb: int = 25
) -> str:  # pragma: no cover
    """
    Simplified API to upload a (vst) file to Drive.
    """
    drive = DriveSingleton()  # will authenticate only on creation of first instance.

    return drive.upload(file_path, filename, folder, chunks_size_mb)
