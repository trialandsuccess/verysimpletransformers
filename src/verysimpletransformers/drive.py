"""
Simple Google Drive API to store models (.vst files).

NOTE: This does not really use pytest, since it is very hard to test with the Google Drive API..
"""
from __future__ import annotations

import io
import os
import re
import typing
import uuid
from pathlib import Path
from typing import Optional, Union

import requests
import tqdm
import yarl
from configuraptor import Singleton
from requests.cookies import RequestsCookieJar
from yarl import URL as _URL

from . import from_vst, to_vst
from .exceptions import BaseVSTException
from .support import as_binaryio
from .types import DummyModel, SimpleTransformerProtocol

CLIENT_ID = "327892950221-uaah9475qfsfp64s6nqa3o15a9eh3p67.apps.googleusercontent.com"
REDIRECT_URI = "https://oauth.trialandsuccess.nl/callback"
SCOPE = "https://www.googleapis.com/auth/drive.file"

AUTH_TOKEN_FILE = ".gdrive_access_token"


class UploadError(BaseVSTException):
    """
    Raised when something goes wrong while uploading to Drive.
    """


def _clean_locals(_locals: dict[str, typing.Any]):
    return {k: v for k, v in _locals.items() if k not in {"self", "session"} and not k.startswith("_")}


def unfinal(method):
    method.__finalized__ = False
    return method


_URL.__init_subclass__ = object.__init_subclass__  # breaking the law

_URL.get = lambda *a, **kw: print("yay")


@unfinal  # breaking the law pt2
class URL(_URL):
    """
    Enhanced version of yarl.URL that also supports HTTP verbs.
    """

    def get(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).get(str(self), **_clean_locals(locals()))

    def options(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).options(str(self), **_clean_locals(locals()))

    def head(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).head(str(self), **_clean_locals(locals()))

    def post(
        self,
        data: Optional[Union[dict, list, bytes]] = None,
        json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        params: Optional[Union[dict, list, bytes]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).post(str(self), **_clean_locals(locals()))

    def put(
        self,
        data: Optional[Union[dict, list, bytes]] = None,
        json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        params: Optional[Union[dict, list, bytes]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).put(str(self), **_clean_locals(locals()))

    def patch(
        self,
        data: Optional[Union[dict, list, bytes]] = None,
        json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        params: Optional[Union[dict, list, bytes]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).patch(str(self), **_clean_locals(locals()))

    def delete(
        self,
        params: Optional[Union[dict, list, bytes]] = None,
        # data: Optional[Union[dict, list, bytes]] = None,
        # json: Optional[Union[int, float, str, bool, None, dict]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[Union[dict, RequestsCookieJar]] = None,
        # files: Optional[dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        verify: Union[bool, str] = True,
        stream: bool = True,
        cert: Optional[Union[str, tuple]] = None,
        # new:
        session: requests.Session | None = None,
    ):
        return (session or requests).delete(str(self), **_clean_locals(locals()))


yarl._url.URL = URL  # I don't think the universe will survive this


def get_size(file_obj: io.BytesIO | io.BufferedReader | typing.BinaryIO):
    if isinstance(file_obj, io.BytesIO):
        return file_obj.getbuffer().nbytes
    else:
        # buffered reader
        return os.fstat(file_obj.fileno()).st_size


class Drive:  # pragma: no cover
    """
    Simplified class that allows authenticate and uploading (multi part).
    """

    token: str
    base_url = URL("https://www.googleapis.com/drive/v3/")
    auth_url = URL("https://accounts.google.com/o/oauth2/v2/auth")
    upload_url = URL("https://www.googleapis.com/upload/drive/v3/")

    def __init__(self, token: str = None, **kw: typing.Any) -> None:
        """
        Provide an existing access_token or be prompted to create one.
        """
        self.token = token or self.authenticate(**kw)
        self.ping()

    def generate_headers(self) -> dict[str, str]:
        """
        After .authenticate(), create default auth header.
        """
        return {
            "Authorization": f"Bearer {self.token}",  # Replace with your access token
            "Content-Type": "application/json; charset=UTF-8",
        }

    def ping(self, session: requests.Session = None):
        """
        Make sure the authentication token works and the API responds normally.
        """
        url = self.base_url / "about" % {"fields": "kind"}
        resp = url.get(headers=self.generate_headers(), timeout=5, session=session)
        return resp.status_code == 200 and resp.json()["kind"] == "drive#about"

    def _load_token(self) -> str:
        with open(AUTH_TOKEN_FILE, "r") as f:
            return f.read()

    def _store_token(self, token: str) -> None:
        with open(AUTH_TOKEN_FILE, "w") as f:
            f.write(token)

    def authenticate_cached(self) -> str | None:
        try:
            self.token = self._load_token()
            self.ping()  # could crash if invalid auth, should do normal authenticate() in that case.
            return self.token
        except Exception:
            return None

    def authenticate(
        self, scope: str = SCOPE, redirect_uri: str = REDIRECT_URI, client_id: str = CLIENT_ID, cache: bool = True
    ) -> str:
        """
        CLI-authenticate: print the URL and prompt for access token.

        Uses oauth.trialandsuccess.nl since a callback URL is required.
         Other methods that do not require a callback, expect a private key or secure config which is not
         feasible for an open source library.
        """
        if cache and (token := self.authenticate_cached()):
            return token

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

        token = input("Please paste your token here: ")

        if cache:
            self._store_token(token)

        return token

    def download(self, file_id: str) -> io.BytesIO:
        url = self.base_url / "files" / file_id
        with requests.Session() as session:
            resp = url.get(session=session)

            print(resp.status_code, resp.headers)

            return io.BytesIO(b"")

    def upload(
        self,
        file_path: str | Path | typing.BinaryIO,
        filename: str = None,
        folder: str = None,
        chunks_size_mb: int = 25,
    ) -> str:
        """
        Upload a file in multiple chunks.

        Returns the new file url.
        """
        if isinstance(file_path, Path):
            file_path = str(file_path.resolve())

        if not filename and isinstance(file_path, str):
            filename = os.path.basename(file_path)

        with requests.Session() as session, as_binaryio(file_path) as file_obj:
            location = self._initialize_upload(filename, folder, session)

            total_size = os.path.getsize(file_path) if isinstance(file_path, str) else get_size(file_obj)
            self._upload_chunks(file_obj, total_size, location, session, chunks_size_mb)

            metadata = self._finalize_upload(location, session)

        return f"https://drive.google.com/file/d/{metadata['id']}/view"

    def _initialize_upload(self, filename: str | None, folder: str | None, session: requests.Session) -> str:
        metadata: dict[str, str | list[str]] = {
            "name": filename or "model.vst",
        }
        if folder:
            metadata["parents"] = [folder]
        resp = session.post(
            str(
                self.upload_url
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

    def _upload_chunks(
        self, file: typing.BinaryIO, total_size: int, location: str, session: requests.Session, chunks_size_mb: int
    ) -> None:
        chunk_size = chunks_size_mb * 1024 * 1024  # 50MB chunk size (you can adjust this)
        with tqdm.tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as progress:
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
    file_path: str | Path | typing.BinaryIO | SimpleTransformerProtocol,
    filename: str = None,
    folder: str = None,
    chunks_size_mb: int = 25,
) -> str:  # pragma: no cover
    """
    Simplified API to upload a (vst) file to Drive.
    """
    drive = DriveSingleton()  # will authenticate only on creation of first instance.

    if isinstance(file_path, SimpleTransformerProtocol):
        file_obj = io.BytesIO()
        to_vst(file_path, file_obj)
        filename = filename or f"{file_path.__class__.__name__}.vst"
    else:
        file_obj = file_path

    return drive.upload(file_obj, filename, folder, chunks_size_mb)


GOOGLE_ID_RE = re.compile(r"[-\w]{25,}")


def _get_google_id(url: str):
    return next(GOOGLE_ID_RE.finditer(url)).group(0)


def from_drive(url_or_id: str) -> SimpleTransformerProtocol:
    drive = DriveSingleton()

    file_id = _get_google_id(url_or_id)

    data = drive.download(file_id)

    return from_vst(data)


def main():
    # model = DummyModel()
    #
    # return to_drive(model)

    model = from_drive("https://drive.google.com/file/d/1r1ETM7GyRwyGw1ziPmymkEtL--Hx2ZwP/view?usp=drive_link")

    result = model.predict(["Hello there"])
    print(result)
    return result
