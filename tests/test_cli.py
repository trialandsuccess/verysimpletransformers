from src.verysimpletransformers.cli import app
from typer.testing import CliRunner

runner = CliRunner(mix_stderr=False)


def test_good():
    result = runner.invoke(app, ["test"])
    assert result.exit_code == 0
    assert "hi" in result.stdout


def test_bad():
    result = runner.invoke(app, ["other"])
    assert result.exit_code == 1
    assert "bye" in result.stdout

def test_unknown():
    result = runner.invoke(app, ["yet_another"])
    assert result.exit_code == 2
