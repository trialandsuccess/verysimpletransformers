from src.verysimpletransformers.cli import _autoselect_action, generate_custom_style

# from typer.testing import CliRunner

from src.verysimpletransformers.support import has_stdin

# runner = CliRunner(mix_stderr=False)


def test_actions():
    # todo: catch stdout
    _autoselect_action([])
    _autoselect_action(["invalid"])
    _autoselect_action(["upgrade something.vst"])

def test_style():
    assert generate_custom_style()
