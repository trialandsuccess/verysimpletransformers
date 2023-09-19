"""This file contains all Typer Commands."""
import typer
from configuraptor.singleton import Singleton
from rich import print
from su6.core import warn, Verbosity, state, DEFAULT_VERBOSITY  # todo: replace these
from typing_extensions import Never
from .__about__ import __version__

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

def version_callback() -> Never:
    """
    --version requested!
    """
    print(f"vst Version: {__version__}")

    raise typer.Exit(0)


def show_config_callback() -> Never:
    """
    --show-config requested!
    """
    print(state)

    raise typer.Exit(0)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: str = None,
    verbosity: Verbosity = DEFAULT_VERBOSITY,
    # stops the program:
    show_config: bool = False,
    version: bool = False,
) -> None:
    """
    This callback will run before every command, setting the right global flags.

    Args:
        ctx: context to determine if a subcommand is passed, etc
        config: path to a different config toml file
        verbosity: level of detail to print out (1 - 3)

        show_config: display current configuration?
        version: display current version?

    """
    if state.config:
        # if a config already exists, it's outdated, so we clear it.
        # we don't clear everything since Plugin configs may be already cached.
        Singleton.clear(state.config)

    state.load_config(config_file=config, verbosity=verbosity)

    if show_config:
        show_config_callback()
    elif version:
        version_callback()
    elif not ctx.invoked_subcommand:
        warn("Missing subcommand. Try `su6 --help` for more info.")
    # else: just continue