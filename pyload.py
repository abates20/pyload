"""
pyload
------

A simple module for small loading animations in the console.
The base class was derived from a
[stackoverflow answer](https://stackoverflow.com/a/66558182).
"""

from itertools import cycle
from threading import Thread
from time import sleep
from shutil import get_terminal_size
import sys
import io
from typing import Literal

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

def getpass(prompt = "Password: "):
    """
    Prompt for a password with echo turned off using
    getpass.getpass. 
    
    Designed to work better with the loaders in this
    module by setting `stream=sys.stdout`. Works best
    with loaders where `print_mode=INLINE`. Loaders
    with `print_mode=NEWLINE` will show the password
    prompt on one line, but the cursor will be located
    on the next line with the loading message.
    """
    from getpass import getpass as _getpass
    return _getpass(prompt, stream=sys.stdout)

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
        self._printed_msg = io.StringIO()
        sys.stdout = self._printed_msg
        self._thread.start()

    def stop(self):
        """
        Stop the loading animation and display the finished message.
        """
        self._done = True
        sys.stdout = STDOUT

        # Clear out the terminal line
        n_cols = get_terminal_size().columns
        print("\r" + " " * n_cols, flush=True, end="")

        # Print the finished message
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
        global INLINE, NEWLINE

        symbol = f"{self._color}{BOLD}{current_symbol}{ENDC}"
        msg = f"{symbol} {self._loading_msg}"

        if self._printed_msg.getvalue():
            printed_msg = self._printed_msg.getvalue().strip("\n").split("\n")[-1]
            if self._print_mode == INLINE:
                msg = msg + " " + printed_msg
            elif self._print_mode == NEWLINE:
                msg = printed_msg + " " * (len(msg) - len(printed_msg)) + "\n" + msg
                self._printed_msg.truncate(0)
            else:
                self._error_in_process = True
                self.stop()
                raise ValueError(f"Unrecognized PRINT_MODE: {self._print_mode}")           
            
        return msg

    @classmethod
    def wrap(cls, loading_msg: str = "Loading...", finished_msg: str = "Done!",
             steptime = 0.1, color = "white"):
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

        Returns
        -------
        A decorator function.
        """
        loader = cls(loading_msg, finished_msg, steptime, color)

        def decorator(func):
            def wrapper(*args, **kwargs):
                with loader:
                    return func(*args, **kwargs)
            return wrapper
        return decorator


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
