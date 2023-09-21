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

if typing.TYPE_CHECKING:
    from .types import AllSimpletransformersModels

app = typer.Typer()
devnull = open(os.devnull, "w")  # noqa: SIM115


def generate_custom_style(
    main_color: str = "green",  # "#673ab7"
    secondary_color: str = "#673ab7",  # "#f44336"
) -> questionary.Style:
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


def show_help() -> None:
    print("Help")


def _run_interactive(model: str | AllSimpletransformersModels) -> None:
    # model prints are hidden by writing to /dev/null
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
                prediction = model.predict(prompt)[0][0]
            print(prediction)
        elif questionary.confirm(
            "Would you like to exit?", default=False, style=generate_custom_style(secondary_color="#f44336")
        ).ask():
            return


def run_stdin(args: list[str]) -> None:
    model_name = args[0]
    print("Loading model", model_name, "...", file=sys.stderr)
    with RedirectStdStreams(stdout=devnull, stderr=devnull):
        model = from_vst(args[0])
    print("Loaded model", model, f"({model_name})", "...", file=sys.stderr)
    for prompt in sys.stdin:
        with RedirectStdStreams(stdout=devnull, stderr=devnull):
            prediction = model.predict(prompt)[0][0]
        print(prediction)


def run_interactive(args: list[str | AllSimpletransformersModels]) -> None:
    return _run_interactive(*args)


DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"


def _serve(filename: str, port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:
    from .serve import MachineLearningModelServer

    print("Loading model", filename, "...", file=sys.stderr)
    with RedirectStdStreams(stdout=devnull, stderr=devnull):
        model = from_vst(filename)

    print(f"Done loading {model}!")
    print(f"Now serving [bright_magenta]{filename}[/bright_magenta] on [cyan]http://{host}:{port}[/cyan]")
    MachineLearningModelServer(host, port).serve_forever(model)


def serve(args: list[str], port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:
    return _serve(args[0], port=port, host=host)


def upgrade(args: list[str]) -> None:
    print("upgrade", args)


def default(_: list[str]) -> None:
    print(" default ")
    print("(show all syntax options)")
    # ./model.vst
    # ./model.vst <action>
    # vst model.vst
    # vst <action> model.vst
    # vst model.vst <action>
    # cat prompts.txt | ./model.vst
    # cat prompts.txt | vst model.vst
    # ./model.vst < prompts.txt
    # vst model.vst < prompts.txt


def clear() -> None:
    os.system("clear")  # nosec


def prompt_user(args: list[str]) -> None:
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


@app.command()
def main(args: list[str] = typer.Argument(None), port: int = 8000, host: str = "localhost") -> None:
    file = ".".join(args)

    iterate = [_ for _ in file.split(".") if _]

    if has_stdin():
        return run_stdin(args)

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
            serve(args, port=port, host=host)

        case [_, "vst", "serve"]:
            args.pop(-1)
            serve(args, port=port, host=host)

        case [_, "vst", "upgrade"]:
            args.pop(-1)
            upgrade(args)

        case _:
            default(args)

    # todo: support stdin: `cat prompt.txt | ./model.vst`, `./model.vst < prompt.txt`
