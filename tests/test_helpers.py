import io
import typing
from pathlib import Path

from src.verysimpletransformers.core import as_binaryio

def test_as_binaryio():
    path = Path("/tmp/pytest_verysimpletransformers_file")
    path.touch()

    assert hasattr(as_binaryio(str(path)), "read")
    assert hasattr(as_binaryio(path), "read")
    assert hasattr(as_binaryio(None), "read")
    assert hasattr(as_binaryio(open(str(path), "rb")), "read")
