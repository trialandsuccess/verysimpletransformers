"""
Stores custom exceptions and the except hook.
"""
import sys
import types
import typing

from rich import print

CorruptionReasons = typing.Literal["compression", "pickling", "unknown"]


class BaseVSTException(Exception):
    """
    All exceptions in this library should inherit from this one.
    """


class CorruptedModelException(BaseVSTException, ValueError):
    """
    Raised when the actual model could not be loaded (ignores metadata).
    """

    reason: CorruptionReasons
    origin: Exception | None

    def __init__(self, reason: CorruptionReasons, origin: Exception = None) -> None:
        """
        Provide the reason it could not be loaded and possibly an origin exception.
        """
        self.reason = reason
        self.origin = origin
        msg = f"The model could not be loaded due to a {reason} error."

        if origin:
            msg += f" [{origin}]"

        super().__init__(msg)


def custom_excepthook(
    exc_type: typing.Type[BaseException], exc_value: BaseException, _: types.TracebackType | None
) -> None:
    """
    Overwrite Typer's default exception hook (in order to hide traceback).
    """
    # Print only the exception message without the traceback
    print(f"[red]{exc_type.__name__}:[/red]", exc_value, file=sys.stderr)
