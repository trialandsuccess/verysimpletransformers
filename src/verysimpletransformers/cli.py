"""This file contains all Typer Commands."""
import os
import sys
import typing

import questionary
import typer
from configuraptor import BinaryConfig
from rich import print

from .core import (
    DEFAULT_COMPRESSION,
    ZeroThroughNine,
    _from_vst,
    from_vst_with_metadata,
    simple_load,
    upgrade_metadata,
)
from .exceptions import CorruptedModelException, custom_excepthook
from .support import RedirectStdStreams, as_binaryio, devnull, has_stdin
from .types import SimpleTransformerProtocol

if typing.TYPE_CHECKING:  # pragma: no cover
    from .types import AllSimpletransformersModels

    ModelOrFilename = typing.Union[str, AllSimpletransformersModels]
else:
    ModelOrFilename = typing.Union[str, "AllSimpletransformersModels"]


app = typer.Typer()


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


def run_interactive(filename: ModelOrFilename) -> None:  # pragma: no cover
    """
    Keep querying the user and process every 'prompt'.

    If an empty line is entered, the user will be prompted if they want to leave.
    The user can also exit with ctrl-d or ctrl-c.
    """
    clear()
    model, model_name = simple_load(filename)

    clear()
    print("Running", model, f"({model_name})" if model_name and model_name != str(model) else "")

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


def run_stdin(filename: str) -> None:  # pragma: no cover
    """
    If the program immediatly gets data, process line by line and print predictions.
    """
    model, model_name = simple_load(filename)

    for prompt in sys.stdin:
        with RedirectStdStreams(stdout=devnull, stderr=devnull):
            prediction = model.predict(prompt)[0][0]
        print(prediction)


DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"


def serve(filename: ModelOrFilename, port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:  # pragma: no cover
    """
    Start a simple HTTP server that responds to queries with model outputs.
    """
    # only local import to reduce overhead on other commands.
    from .serve import MachineLearningModelServer

    model, model_name = simple_load(filename)

    print(f"Now serving [bright_magenta]{model_name}[/bright_magenta] on [cyan]http://{host}:{port}[/cyan]")
    MachineLearningModelServer(host, port).serve_forever(model)


def upgrade(
    filename: str, output_file: str = None, compression: ZeroThroughNine | int = DEFAULT_COMPRESSION
) -> None:  # pragma: no cover
    """
    Upgrade the metadata of a model to the latest version.
    """
    output_file = output_file or filename
    upgrade_metadata(filename, output_file, compression=typing.cast(ZeroThroughNine, compression))


def show_info(filename: str) -> None:
    """
    Show metadata info about this model.
    """
    error = ""
    try:
        model, meta, valid = from_vst_with_metadata(filename)
    except CorruptedModelException as e:
        # just load metadata
        error = str(e)
        with as_binaryio(filename) as f:
            model, meta, valid = _from_vst(f, with_metadata=True, with_model=False)

    def show_recursive(obj: typing.Any, level: int = 0) -> None:
        for option, value in obj.__dict__.items():
            if option.startswith("_"):
                continue
            if isinstance(value, BinaryConfig):
                print("\t" * level, f"[yellow]{option}[/yellow] ▼")
                show_recursive(value, level + 1)
            else:
                print("\t" * level, f"[yellow]{option}[/yellow] =", value)

    show_recursive(meta)
    print("[yellow]model loaded properly:[/yellow]", isinstance(model, SimpleTransformerProtocol))
    if error:
        print("[red]error:[/red]", error)


def show_help(with_welcome: bool = True) -> None:
    """
    If simply `vst` is executed, welcome the user and show possible options.

    If an invalid command is used, `default` will be executed which will call this function with with_welcome=False.
    """
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
    print("    --port <PORT>, -p <PORT>     Specify the port number (default: 8000)")
    print("    --host <HOST>, -h <HOST>     Specify the host (default: 'localhost')")
    print("- 'upgrade': Upgrade the metadata of a model to the latest version.")
    print("  Options for 'upgrade':")
    print(
        "    --output <FILE>,       -o <FILE>      Specify which file the upgraded model will be written to "
        "(default: overwrite input file)"
    )
    print(
        f"    --compression <LEVEL>, -c <LEVEL>     Specify the level of compression "
        f"(default: {DEFAULT_COMPRESSION} or previous value)"
    )
    print("- 'show': Show the metadata stored in the model file.")

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
    model_name = args[0]
    questionary.print(model_name, style="bold italic fg:green")

    # with RedirectStdStreams(stdout=devnull, stderr=devnull):
    model, metadata, valid_meta = from_vst_with_metadata(model_name)

    choice = questionary.select(
        "What do you want to do?",
        choices=[
            questionary.Choice("Run", "run", shortcut_key="r"),
            questionary.Choice("Serve", "serve", shortcut_key="s"),
            questionary.Choice(
                "Upgrade", "upgrade", disabled="Fully up-to-date!" if valid_meta else None, shortcut_key="u"
            ),
            questionary.Choice("Exit", None, shortcut_key="e"),
        ],
        use_shortcuts=True,
        use_arrow_keys=True,
        style=generate_custom_style(),
    ).ask()

    match choice:
        case "run":
            run_interactive(model)
        case "serve":
            serve(model)
        case "upgrade":
            upgrade(model_name)
        case None:
            # = exit or ctrl-c
            return


@app.command()
def main(
    args: list[str] = typer.Argument(None),
    port: typing.Annotated[int, typer.Option("--port", "-p")] = DEFAULT_PORT,
    host: typing.Annotated[str, typer.Option("--host", "-h")] = DEFAULT_HOST,
    output: typing.Annotated[str, typer.Option("--output", "-o")] = None,
    compression: typing.Annotated[int, typer.Option("--compression", "-c")] = DEFAULT_COMPRESSION,
) -> None:  # pragma: no cover
    """
    Cli entrypoint.
    """
    sys.excepthook = custom_excepthook

    if has_stdin():
        return run_stdin(args[0])

    file = ".".join(args)

    iterate = [_ for _ in file.split(".") if _]
    match iterate:
        case []:
            show_help()

        case [_, "vst"]:
            # vst file!
            prompt_user(args)

        case ["run", _, "vst"]:
            run_interactive(args[1])

        case [_, "vst", "run"]:
            run_interactive(args[0])

        case ["serve", _, "vst"]:
            serve(args[1], port=port, host=host)

        case [_, "vst", "serve"]:
            serve(args[0], port=port, host=host)

        case ["upgrade", _, "vst"]:
            upgrade(args[1], output_file=output, compression=compression)

        case [_, "vst", "upgrade"]:
            upgrade(args[0], output_file=output, compression=compression)

        case ["show", _, "vst"]:
            show_info(args[1])

        case [_, "vst", "show"]:
            show_info(args[0])

        case _:
            default(args)
