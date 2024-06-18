from itertools import cycle
from threading import Thread
from time import sleep
from shutil import get_terminal_size

COLORS = {
    "white": "",
    "purple": "\033[94m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m"
}
BOLD = "\033[1m"
ENDC = "\033[0m"

class BaseLoader:
    """
    The base class for small loading animations in the console.
    """

    _steps = ["|", "/", "-", "\\"]

    def __init__(self, loading_msg: str = "Loading...", finished_msg: str = "Done!",
                 timeout = 0.1, color = "white"):
        """
        Initialize the BaseLoader.

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

        self._thread = Thread(target=self._animate)
        self._done = False
        self._error_in_process = False

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type:
            self._error_in_process = True
        self.stop()

    def start(self):
        self._thread.start()

    def stop(self):
        self._done = True

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
            print(f"\r{symbol} {self._loading_msg}", flush=True, end="")
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


class SpinLoader(BaseLoader):
    pass

class DotLoader(BaseLoader):
    _steps = ["⡆", "⠇", "⠋", "⠙", "⠸", "⢰", "⣠", "⣄"]