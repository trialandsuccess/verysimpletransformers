import io
from pathlib import Path

from src.verysimpletransformers.core import as_binaryio


def test_as_binaryio():
    path = Path("/tmp/pytest_verysimpletransformers_file")
    path.touch()

    with as_binaryio(str(path)) as f:
        assert hasattr(f, "read")

    with as_binaryio(path) as f:
        assert hasattr(f, "read")

    with as_binaryio(open(str(path), "rb")) as f:
        assert hasattr(f, "read")

    with as_binaryio(io.BytesIO()) as f:
        assert hasattr(f, "read")

    with as_binaryio(None) as f:
        assert hasattr(f, "read")
