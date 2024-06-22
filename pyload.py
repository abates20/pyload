"""
pyload
------

A simple module for small loading animations in the console.
The base class was derived from a
[stackoverflow answer](https://stackoverflow.com/a/66558182).

Includes some rudimentary handling of things printed to the
console while a loader is running. Two modes for this are
available: INLINE (default) and NEWLINE. With INLINE mode,
printed messages will appear in the console on the same line
as the loading message (to the right of the loading message).
Each time something new is printed, it will replace what was
printed before. With NEWLINE mode, each time a message is
printed, the loading animation will shift down one row and the
message will occupy the row where the animation previousy was.

Two functions for receiving user input are provided that are
designed to be more compatible with the loading animations
than their standard counterparts: `input` and `getpass`.
The standard `getpass` function can also be used if the `stream`
parameter is set to `sys.stdout`.
"""

from itertools import cycle
from threading import Thread
from typing import Literal
from time import sleep
from shutil import get_terminal_size
import sys, io

COLORS = {
    "white": "",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "darkcyan": "\033[36m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m"
}
BOLD = "\033[1m"
ENDC = "\033[0m"

STDOUT = sys.__stdout__

INLINE = "INLINE"
NEWLINE = "NEWLINE"
_PRINT_MODES = Literal["INLINE", "NEWLINE"]

__user_input__ = False
_active_loader = None

def input(prompt = ""):
    """
    Read a string from standard input.

    > Note: currently only functional on MacOS and Linux.
    
    Intended to behave identically to the standard python 
    `input` function under normal circumstances while
    also being compatible with loading animations.

    Works best with loaders that have `print_mode=INLINE`.
    Loaders with `print_mode=NEWLINE` will behave like
    INLINE loaders while input is being read.
    """
    import tty, sys, termios

    # Set __user_input__ to True
    global __user_input__, _active_loader
    __user_input__ = True
    
    # Print the prompt
    print(prompt, end=" \b", flush=True)    # end=" \b" prevents the previous
                                            # thing printed from being displayed
                                            # if the prompt is ""

    # Set the terminal to cbreak and no echo
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    # Read and display input characters
    input_chars = []
    while True:
        char = sys.stdin.read(1)
        if char in ["\n", "\r"]:
            break
        elif char in ["\b", "\x7f"]:
            if input_chars: 
                input_chars.pop()
                print("\b \b", end="", flush=True)
        else:
            input_chars.append(char)
            print(char, end="", flush=True)

    # Reset the terminal
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

    # Stick "\n" on the end of what is being displayed in the terminal
    # so the next print statement is kept separate
    print()

    # Set __user_input__ back to False and wait for the active loader to go to its next step
    __user_input__ = False
    if isinstance(_active_loader, _BaseLoader): sleep(_active_loader._steptime)

    return "".join(input_chars)

def getpass(prompt = "Password: "):
    """
    Prompt for a password with echo turned off using
    getpass.getpass. 
    
    Designed to work better with the loaders in this
    module by setting `stream=sys.stdout`. Works best
    with loaders where `print_mode=INLINE`. Loaders
    with `print_mode=NEWLINE` will temporarily work
    like an INLINE loader while input is being read.
    """
    from getpass import getpass as _getpass

    # Set __user_input__ to True
    global __user_input__
    __user_input__ = True

    password = _getpass(prompt, stream=sys.stdout)

    # Set __user_input__ back to False and wait for the active loader to go to its next step
    __user_input__ = False
    if isinstance(_active_loader, _BaseLoader): sleep(_active_loader._steptime)

    return password 

def _clear_line():
    """
    Clear out the current terminal line.
    """
    n_cols = get_terminal_size().columns
    print("\r" + " " * n_cols, flush=True, end="", file=STDOUT)


class _BaseLoader:
    """
    The base class for small loading animations in the console.
    """

    _steps = ["|", "/", "-", "\\"]

    def __init__(self, loading_msg: str = "Loading...", finished_msg: str = "Done!",
                 steptime = 0.1, color = "white", print_mode: _PRINT_MODES = INLINE):
        """
        Initialize the Loader.

        Parameters
        ----------
        loading_msg : str
            The message to display while the loader is running.
        finished_msg : str
            The message to display when the loader finishes.
        steptime : float
            How long to pause between each step in the animation.
        color : str
            The color of the animation. Options are 'white', 'blue', 'purple', 
            'cyan', 'darkcyan', 'green', 'yellow', and 'red'.
        print_mode : "INLINE" | "NEWLINE"
            The method for displaying printed values while a loader is running.
            Options are "INLINE" or "NEWLINE"
        """
        self._loading_msg: str = loading_msg
        self._finished_msg: str = finished_msg
        self._steptime = steptime
        self._color = COLORS.get(color, "")
        self._print_mode = print_mode
        assert print_mode in [INLINE, NEWLINE], f"Unrecognized print_mode: {print_mode}"

        self._thread: Thread = Thread(target=self._animate, daemon=True)
        self._done = False
        self._error_in_process = False
        self._formatter = _MsgFormatter(print_mode)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type:
            self._error_in_process = True
        self.stop()

    def start(self):
        """
        Start the loading animation.
        """
        # Set the active loader
        global _active_loader
        _active_loader = self

        self._printed_msg = io.StringIO()
        sys.stdout = self._printed_msg
        self._thread.start()

    def stop(self):
        """
        Stop the loading animation and display the finished message.
        """
        # Reset the active loader
        global _active_loader
        _active_loader = None

        # Stop the loader and reset STDOUT
        self._done = True
        sys.stdout = STDOUT

        # Print the finished message
        _clear_line()
        if not self._error_in_process:
            print(f"\r{self._finished_msg}", flush=True)
        else:
            print(f"\r", flush=True)

    def _animate(self):
        for x in cycle(self._steps):
            if self._done:
                break
            print(f"\r{self._get_msg(x)}", flush=True, end="", file=STDOUT)
            sleep(self._steptime)

    def _get_msg(self, current_symbol):
        symbol = f"{self._color}{BOLD}{current_symbol}{ENDC}"
        loader_msg = f"{symbol} {self._loading_msg}"          
        return self._formatter.format(loader_msg, self._printed_msg)

    @classmethod
    def wrap(cls, loading_msg: str = "Loading...", finished_msg: str = "Done!",
             steptime = 0.1, color = "white", print_mode: _PRINT_MODES = INLINE):
        """
        Create a decorator to wrap a defined function with a loading animation.
        
        
        The animation gets displayed with the provided loading message while the
        function runs. Once the function is finished, the finished message replaces
        the loading animation/message.

        Parameters
        ----------
        loading_msg : str
            The message to display while the function is running.
        finished_msg : str
            The message to display when the function finishes.
        steptime : float
            How long to pause between each step in the animation.
        color : str
            The color of the animation. Options are 'white', 'blue', 'purple', 
            'cyan', 'darkcyan', 'green', 'yellow', and 'red'.
        print_mode : "INLINE" | "NEWLINE"
            The method for displaying printed values while a loader is running.
            Options are "INLINE" or "NEWLINE"

        Returns
        -------
        A decorator function.
        """
        loader = cls(loading_msg, finished_msg, steptime, color, print_mode)

        def decorator(func):
            def wrapper(*args, **kwargs):
                with loader:
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    

class _MsgFormatter:
    """
    A class for formatting loading messages with printed stuff.
    """

    def __init__(self, print_mode: _PRINT_MODES):
        self._print_mode = print_mode
        self._printed_lines = []

    def format(self, loader_msg: str, stdio: io.StringIO):
        """
        Format the loader message and any printed statements for
        display based on the current printing mode ("INLINE" or 
        "NEWLINE"). Printing mode is specified when the formatter
        is initialized.

        Parameters
        ----------
        loader_msg : str
            The current symbol and loading message for the loader.
        stdio : io.StringIO
            The StringIO object that sys.stdout has been pointed
            to for capturing printed strings.

        Returns
        -------
        str
            The formatted string for printing to the console.
        """
        printed_msg = self._get_printed_msg(stdio)
        
        if not printed_msg is None:
            _clear_line()
            if self._print_mode == INLINE or __user_input__:
                return f"{loader_msg} {printed_msg}"
            return f"{printed_msg}\n{loader_msg}"
        
        return loader_msg

    def _get_printed_msg(self, stdio: io.StringIO):
        """
        Gets the printed message to be displayed (if there is one).
        """
        global INLINE
        if stdio.getvalue():
            printed_lines = stdio.getvalue().strip("\n").split("\n")
            last_printed = printed_lines[-1]

            # For INLINE printing you always just want whatever was last printed
            if self._print_mode == INLINE or __user_input__:
                return last_printed
            
            # For NEWLINE printing you just want to send back a line the first time
            # it gets seen (otherwise you keep printing a ton of new lines)
            last_seen = self._printed_lines[-1] if len(self._printed_lines) > 0 else None
            if last_printed != last_seen:
                
                # Update the seen lines
                if len(printed_lines) == len(self._printed_lines):
                    self._printed_lines[-1] = last_printed
                else:
                    self._printed_lines.append(last_printed)

                return last_printed
            
        return


class SpinLoader(_BaseLoader):
    """
    A basic spinning bar loader.

    Cycles through these symbols: |, /, -, \\
    """
    pass

class DotLoader(_BaseLoader):
    """
    A loader comprised of three circling dots.

    Cycles through these symbols: ⡆, ⠇, ⠋, ⠙, ⠸, ⢰, ⣠, ⣄
    """
    _steps = ["⡆", "⠇", "⠋", "⠙", "⠸", "⢰", "⣠", "⣄"]

class CaretLoader(_BaseLoader):
    """
    A loader comprised of the caret symbol spinning in a circle.

    Cycles through these sybmols: ^, ›, ⌄, ‹
    """
    _steps = [" ^ ", "  ›", " ⌄ ", "‹  "]

class ArrowLoader(_BaseLoader):
    """
    A sliding arrow loader.

    Cycles through these symbols: >----, ->---, -->--, --->-, ---->, -----
    """
    _steps = [">----", "->---", "-->--", "--->-", "---->", "-----"]

class AppleLoader(_BaseLoader):
    """
    A loader with an apple symbol () sliding back and forth.
    """
    _steps = ["    ", "    ", "    ", "    ", "    ", "    ", "    ", "    "]

class SlidingLoader(_BaseLoader):
    """
    A loader with a row of equal signs sliding from side to side.
    """
    _steps = ["=    ", "==   ", "===  ", "==== ", " ====", "  ===", "   ==", "    =",
              "    =", "   ==", "  ===", " ====", "==== ", "===  ", "==   ", "=    "]
    
class SlidingLoader2(_BaseLoader):
    """
    A loader with a row of dashes sliding from side to side.
    """
    _steps = ["—    ", "——   ", "———  ", "———— ", " ————", "  ———", "   ——", "    —",
              "    —", "   ——", "  ———", " ————", "———— ", "———  ", "——   ", "—    "]
