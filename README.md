# pyload

> Author: Adam Bates (abates20)  
> Last Updated: 18 June 2024

Pyload is a very simple and basic python module for displaying
loading animations in the console while code is executing. It
takes advantage of the threading module to run the animation
in a separate thread, allowing the animation to be displayed 
while other code is running simultaneously.

![pyload_example](https://github.com/abates20/pyload/assets/131566916/14bda00c-e548-4cb5-a224-8b3ff5d2a935)

## Installation

```
pip install pyload@git+https://github.com/abates20/pyload.git
```

## Usage

There are several available loaders that all inherit from the
same base Loader class and thus function the same. The primary
way to use a loader is through context management:

```python
from pyload import SpinLoader

with SpinLoader():
  # Do some things
```

Upon entering the `with` block, the loading animation will be
displayed in the console. When the `with` block is exited, the
animation will disappear and be replaced by the finish message
("Done!"). If the code exits the block due to an error, the
animation will still disappear, but the finish message will not
be printed.

> [!TIP]  
> The loading message, finish message, and color of the animation
> can all be specified:

```python
from pyload import SpinLoader

loader = SpinLoader(
  loading_msg = "Doing some cool stuff...",
  finished_msg = "Yay! We finished!",
  color = "green"
)

with loader:
  # Do cool things
```

If you simply want to put the loader around a function, you can
use the `wrap` method to create a decorator that will wrap your
function in a loader (i.e., the loader starts when the function
is called and stops when the function is exited).

```python
from pyload import DotLoader

@DotLoader.wrap() # put customizations in the wrap method
def my_function():
  # Do stuff
  return
```
