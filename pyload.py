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

class _BaseLoader:
    """
    The base class for small loading animations in the console.
    """

    _steps = ["|", "/", "-", "\\"]

    def __init__(self, loading_msg: str = "Loading...", finished_msg: str = "Done!",
                 timeout = 0.1, color = "white"):
        """
        Initialize the Loader.

        Parameters
        ----------
        loading_msg : str
            The message to display while the loader is running.
        finished_msg : str
            The message to display when the loader finishes.
        timeout : float
            How long to pause between each step in the animation.
        color : str
            The color of the animation. Options are 'white', 'purple', 'cyan',
            'green', 'yellow', and 'red'.
        """
        self._loading_msg: str = loading_msg
        self._finished_msg: str = finished_msg
        self._timeout = timeout
        self._color = COLORS.get(color, "")

        self._thread = Thread(target=self._animate, daemon=True)
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
        self._done = False
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

            symbol = f"{self._color}{BOLD}{x}{ENDC}"
            msg = self._loading_msg
            if self._printed_msg.getvalue():
                printed_msgs = self._printed_msg.getvalue().strip("\n").split("\n")
                msg += " " + printed_msgs[-1]

            print(f"\r{symbol} {msg}", flush=True, end="", file=STDOUT)
            sleep(self._timeout)

    @classmethod
    def wrap(cls, loading_msg: str = "Loading...", finished_msg: str = "Done!",
             timeout = 0.1, color = "white"):
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
        timeout : float
            How long to pause between each step in the animation.
        color : str
            The color of the animation. Options are 'white', 'purple', 'cyan',
            'green', 'yellow', and 'red'.

        Returns
        -------
        A decorator function.
        """
        loader = cls(loading_msg, finished_msg, timeout, color)

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
