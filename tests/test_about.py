import re

from src.verysimpletransformers.__about__ import __version__


def test_version():
    assert __version__
    assert re.match(r"\d+\.\d+\.\d+", __version__)
