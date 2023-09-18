"""This file contains all Typer Commands."""

import typer
from rich import print

app = typer.Typer()


@app.command()
def test() -> None:
    print("hi")
