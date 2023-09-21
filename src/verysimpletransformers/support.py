"""
Helper functionality.
"""

import io
import select
import sys
import typing
from io import BytesIO
from pathlib import Path
from types import TracebackType

import torch
from dill import Unpickler  # nosec


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

    def find_class(self, module: str, name: str) -> typing.Any:  # pragma: no cover
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


class DummyTqdm:  # pragma: no cover
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


class RedirectStdStreams:
    def __init__(self, stdout: typing.TextIO = None, stderr: typing.TextIO = None) -> None:
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self) -> None:
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type: typing.Type[Exception], exc_value: Exception, traceback: TracebackType) -> None:
        self._stdout.flush()
        self._stderr.flush()

        print(self, exc_type, exc_value, traceback)

        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


def has_stdin() -> bool:
    return bool(
        select.select(
            [
                sys.stdin,
            ],
            [],
            [],
            0.0,
        )[0]
    )
