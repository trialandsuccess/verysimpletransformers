"""
Helper to input() with history (arrow up-down) behavior.
"""

import readline
import typing


def input_with_history(prompt: str = "> ") -> typing.Generator[str, None, None]:  # pragma: no cover
    """
    Keeps querying user for input until 'quit', 'exit', ctrl-c or ctrl-d is inputed.

    Uses readline history (like a bash or python shell) so the user can navigate earlier inputs.

    Example:
         for prompt in input_with_history("Please enter something: "):
            print("You entered ", prompt)
    """
    while True:
        try:
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            user_input = "quit"

        # Add the input to the history
        readline.add_history(user_input)

        if user_input in {"quit", "exit"}:
            return
        elif user_input == "history":
            # Print the command history
            history_len = readline.get_current_history_length()
            for i in range(history_len):
                print(f"{i + 1}: {readline.get_history_item(i)}")
        else:
            yield user_input


# variant with persistant history file (rename function above to _handle_input):

# def input_with_history(prompt: str = "> "):  # pragma: no cover
#     # Set a history file for persistent history across sessions
#     readline.set_history_length(100)  # Set the maximum history length
#
#     with tempfile.NamedTemporaryFile() as history_file_obj:
#         history_file = history_file_obj.name
#         with contextlib.suppress(FileNotFoundError):
#             # Try to load history from a file,
#             # or start with empty history
#             readline.read_history_file(history_file)
#
#         try:
#             yield from _handle_input(prompt)
#         finally:
#             # Save the history to the history file
#             readline.write_history_file(history_file)
