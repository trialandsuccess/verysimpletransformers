"""This file contains all Typer Commands."""

import typer
from rich import print

app = typer.Typer()


@app.command()
def test() -> None:
    """
    Demo function.
    """
    print("hi")


@app.command()
def other() -> None:
    """
    Demo error function.
    """
    print("bye")
    0 / 0
