from pathlib import Path

from src.verysimpletransformers.cli import (
    default,
    generate_custom_style,
    show_help,
    upgrade, show_info,
)
from tests.helpers_for_test import _get_corrupted_vst, _get_v0_dummy, _get_v1_dummy


# note: most of CLI is interactive, so no tests were written for it!


def test_actions(capsys):
    show_help()
    captured = capsys.readouterr()

    assert "Welcome to VerySimpleTransformers" in captured.out
    assert "You can use 'verysimpletransformers'" in captured.out

    default([])
    captured = capsys.readouterr()
    assert "Invalid arguments" in captured.out
    assert "Welcome to VerySimpleTransformers" not in captured.out
    assert "You can use 'verysimpletransformers'" in captured.out

def test_show_info(capsys):
    fp = Path("pytest0.vst")
    _get_v0_dummy(fp)

    # v0
    show_info("pytest0.vst")
    captured = capsys.readouterr().out

    assert "error:" not in captured
    assert "verysimpletransformers_version" not in captured

    # v1
    fp = Path("pytest1.vst")
    _get_v1_dummy(fp)

    show_info("pytest1.vst")
    captured = capsys.readouterr().out

    assert "error:" not in captured
    assert "verysimpletransformers_version" in captured

    file = _get_corrupted_vst(reason="compression")

    with file as f:
        show_info(f)
    captured = capsys.readouterr().out

    assert "error:" in captured
    assert "verysimpletransformers_version" in captured


def test_style():
    assert generate_custom_style()
