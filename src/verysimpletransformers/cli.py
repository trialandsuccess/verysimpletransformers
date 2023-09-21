"""This file contains all Typer Commands."""
from __future__ import annotations

import os
import sys
import typing

import questionary
import typer
from rich import print

from .core import from_vst
from .support import RedirectStdStreams, has_stdin

if typing.TYPE_CHECKING:  # pragma: no cover
    from .types import AllSimpletransformersModels

app = typer.Typer()
devnull = open(os.devnull, "w")  # noqa: SIM115


def generate_custom_style(
    main_color: str = "green",  # "#673ab7"
    secondary_color: str = "#673ab7",  # "#f44336"
) -> questionary.Style:
    """
    Reusable questionary style for all prompts of this tool.

    Primary and secondary color can be changed, other styles stay the same for consistency.
    """
    return questionary.Style(
        [
            ("qmark", f"fg:{main_color} bold"),  # token in front of the question
            ("question", "bold"),  # question text
            ("answer", f"fg:{secondary_color} bold"),  # submitted answer text behind the question
            ("pointer", f"fg:{main_color} bold"),  # pointer used in select and checkbox prompts
            ("highlighted", f"fg:{main_color} bold"),  # pointed-at choice in select and checkbox prompts
            ("selected", "fg:#cc5454"),  # style for a selected item of a checkbox
            ("separator", "fg:#cc5454"),  # separator in lists
            ("instruction", ""),  # user instructions for select, rawselect, checkbox
            ("text", ""),  # plain text
            ("disabled", "fg:#858585 italic"),  # disabled choices for select and checkbox prompts
        ]
    )


def _run_interactive(model: str | AllSimpletransformersModels) -> None:  # pragma: no cover
    """
    Keep querying the user and process every 'prompt'.

    If an empty line is entered, the user will be prompted if they want to leave.
    The user can also exit with ctrl-d or ctrl-c.
    """
    clear()
    print("Loading", model)
    if isinstance(model, str):
        # not a model instance yet.
        model_name = model
        model = from_vst(model)
    else:
        model_name = ""

    clear()
    print("Running", model, f"({model_name})" if model_name else "")

    while True:
        if prompt := questionary.text("", style=generate_custom_style(secondary_color="")).ask():
            with RedirectStdStreams(stdout=devnull, stderr=devnull):
                # model prints are hidden by writing to /dev/null

                prediction = model.predict(prompt)[0][0]
            print(prediction)
        elif questionary.confirm(
            "Would you like to exit?", default=False, style=generate_custom_style(secondary_color="#f44336")
        ).ask():
            return


def run_interactive(args: list[str | AllSimpletransformersModels]) -> None:  # pragma: no cover
    """
    Wrapper around _run_interactive to pass the model name from cli args.
    """
    return _run_interactive(*args)


def run_stdin(args: list[str]) -> None:  # pragma: no cover
    """
    If the program immediatly gets data, process line by line and print predictions.
    """
    model_name = args[0]
    print("Loading model", model_name, "...", file=sys.stderr)
    with RedirectStdStreams(stdout=devnull, stderr=devnull):
        model = from_vst(args[0])
    print("Loaded model", model, f"({model_name})", "...", file=sys.stderr)
    for prompt in sys.stdin:
        with RedirectStdStreams(stdout=devnull, stderr=devnull):
            prediction = model.predict(prompt)[0][0]
        print(prediction)


DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"


def _serve(filename: str, port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:  # pragma: no cover
    """
    Start a simple HTTP server that responds to queries with model outputs.
    """
    # only local import to reduce overhead on other commands.
    from .serve import MachineLearningModelServer

    print("Loading model", filename, "...", file=sys.stderr)
    with RedirectStdStreams(stdout=devnull, stderr=devnull):
        model = from_vst(filename)

    print(f"Done loading {model}!")
    print(f"Now serving [bright_magenta]{filename}[/bright_magenta] on [cyan]http://{host}:{port}[/cyan]")
    MachineLearningModelServer(host, port).serve_forever(model)


def serve(args: list[str], port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:  # pragma: no cover
    """
    Wrapper around _serve to pass the model name from cli args.
    """
    return _serve(args[0], port=port, host=host)


def upgrade(args: list[str]) -> None:
    """
    Upgrade the metadata of a model to the latest version.
    """
    print("upgrade", args)


def show_help(with_welcome=True):
    # Introduction
    if with_welcome:
        print("Welcome to VerySimpleTransformers CLI!")

    print("You can use 'verysimpletransformers' or 'vst' interchangeably.")

    # Basic usage examples with vst and verysimpletransformers options
    print("\nBasic Usage:")
    print("  verysimpletransformers model.vst")
    print("  verysimpletransformers <action> model.vst")
    print("  verysimpletransformers model.vst <action>")
    print("  vst model.vst")
    print("  vst <action> model.vst")
    print("  vst model.vst <action>")
    print("  ./model.vst")
    print("  ./model.vst <action>")

    # Explanation of available <action> options
    print("\nAvailable <action> options:")
    print("- 'run': Run the model interactively by typing prompts.")
    print("- 'serve': Start a simple HTTP server to serve model outputs.")
    print("  Options for 'serve':")
    print("    --port <PORT>     Specify the port number (default: 8000)")
    print("    --host <HOST>     Specify the host (default: 'localhost')")
    print("- 'upgrade': Upgrade the metadata of a model to the latest version.")

    print("\nExample:")
    print("$ vst serve ./classification.vst")

    # Additional notes
    print("\nNotes:")
    print("- A .vst file (e.g., 'model.vst') is required for most commands.")
    print("- You can specify <action>, which can be one of the available options mentioned above.")
    print("- If you leave the <action> empty, a dropdown menu will appear for you to select from.")
    print("- You can use 'vst' or 'verysimpletransformers' interchangeably.")


def default(args: list[str]) -> None:
    """
    Invalid command passed, show all syntax options.
    """
    print(f"Invalid arguments {args}. Here are the available syntax options:\n")

    show_help(with_welcome=False)


def clear() -> None:  # pragma: no cover
    """
    Remove previous terminal output.
    """
    os.system("clear")  # nosec


def prompt_user(args: list[str]) -> None:  # pragma: no cover
    """
    If a model was passed to the cli without an action, the user gets a dropdown of options.
    """
    clear()
    questionary.print(args[0], style="bold italic fg:green")

    choice = questionary.select(
        "What do you want to do?",
        choices=[
            questionary.Choice("Run", "run", shortcut_key="r"),
            questionary.Choice("Serve", "serve", shortcut_key="s"),
            questionary.Choice("Upgrade", "upgrade", disabled="Fully up-to-date!", shortcut_key="u"),
            questionary.Choice("Exit", None, shortcut_key="e"),
        ],
        use_shortcuts=True,
        use_arrow_keys=True,
        style=generate_custom_style(),
    ).ask()

    match choice:
        case None:
            return
        case "run":
            run_interactive(args)
        case "serve":
            serve(args)
        case "upgrade":
            upgrade(args)


def _autoselect_action(args: list[str], **kwargs):
    file = ".".join(args)

    iterate = [_ for _ in file.split(".") if _]
    match iterate:
        case []:
            show_help()

        case [_, "vst"]:
            # vst file!
            prompt_user(args)

        case ["run", _, "vst"]:
            args.pop(0)
            run_interactive(args)

        case [_, "vst", "run"]:
            args.pop(-1)
            run_interactive(args)

        case ["serve", _, "vst"]:
            args.pop(0)
            serve(args, port=kwargs['port'], host=kwargs['host'])

        case [_, "vst", "serve"]:
            args.pop(-1)
            serve(args, port=kwargs['port'], host=kwargs['host'])

        case ["upgrade", _, "vst"]:
            args.pop(-1)
            upgrade(args)

        case [_, "vst", "upgrade"]:
            args.pop(-1)
            upgrade(args)

        case _:
            default(args)


@app.command()
def main(args: list[str] = typer.Argument(None), port: DEFAULT_PORT = 8000, host: str = DEFAULT_HOST) -> None:
    """
    Cli entrypoint.
    """
    if has_stdin():
        return run_stdin(args)

    return _autoselect_action(args, port=port, host=host)
