"""This file contains all Typer Commands."""
from typing import Optional

import typer
from configuraptor.singleton import Singleton
from rich import print
from su6.core import DEFAULT_VERBOSITY, Verbosity, state, warn  # todo: replace these
from typing_extensions import Never

from .__about__ import __version__
from .core import from_vst

app = typer.Typer()


def show_help():
    print("Help")


def run(args: list[str]):
    print("run", args)


def serve(args: list[str]):
    from http.server import HTTPServer

    from .serve import MachineLarningModelHandler, MachineLarningModelServer

    (filename,) = args

    model = from_vst(filename)

    port = 8000

    print("serving", [filename], "on port", 8000)
    MachineLarningModelServer("localhost", port).serve_forever(model)


def upgrade(args: list[str]):
    print("upgrade", args)


def default(args: list[str]):
    print(" default ")


@app.command()
def main(args: list[str] = typer.Argument(None)):
    file = ".".join(args)

    iterate = [_ for _ in file.split(".") if _]

    match iterate:
        case []:
            show_help()

        case [_, "vst"]:
            # vst file!
            run(args)

        case ["run", _, "vst"]:
            args.pop(0)
            run(args)

        case ["serve", _, "vst"]:
            args.pop(0)
            serve(args)

        case ["upgrade", _, "vst"]:
            args.pop(0)
            upgrade(args)

        case _:
            default(args)


#
#
# @app.command()
# def test() -> None:
#     """
#     Demo function.
#     """
#     print("hi")
#
#
# @app.command()
# def other() -> None:
#     """
#     Demo error function.
#     """
#     print("bye")
#     0 / 0
#
#
# def version_callback() -> Never:
#     """
#     --version requested!
#     """
#     print(f"vst Version: {__version__}")
#
#     raise typer.Exit(0)
#
#
# def show_config_callback() -> Never:
#     """
#     --show-config requested!
#     """
#     print(state)
#
#     raise typer.Exit(0)
#
#
# @app.callback(invoke_without_command=True, no_args_is_help=True)
# def main(
#     ctx: typer.Context,
#     config: str = None,
#     verbosity: Verbosity = DEFAULT_VERBOSITY,
#     # stops the program:
#     show_config: bool = False,
#     version: bool = False,
# ) -> None:
#     """
#     This callback will run before every command, setting the right global flags.
#
#     Args:
#         ctx: context to determine if a subcommand is passed, etc
#         config: path to a different config toml file
#         verbosity: level of detail to print out (1 - 3)
#
#         show_config: display current configuration?
#         version: display current version?
#
#     """
#     if state.config:
#         # if a config already exists, it's outdated, so we clear it.
#         # we don't clear everything since Plugin configs may be already cached.
#         Singleton.clear(state.config)
#
#     state.load_config(config_file=config, verbosity=verbosity)
#
#     if show_config:
#         show_config_callback()
#     elif version:
#         version_callback()
#     elif not ctx.invoked_subcommand:  # pragma: no cover
#         warn("Missing subcommand. Try `vst --help` for more info.")
#     # else: just continue
