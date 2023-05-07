"""The API wrapper for sending data to the CubeServer server
See https://github.com/snorklerjoe/CubeServer-api-circuitpython for more info!

Supported implementations: cpython, circuitpython
"""

from ._version import *
from sys import implementation as _implementation

# Generic time tools:
from . import timetools

# Check the implementation to use
if   _implementation.name == 'circuitpython':
    # Use the CircuitPython version:
    from .implementations.circuitpy import *

    # Import IR stuff:
    from . import timeout
    from . import irrx

elif _implementation.name == 'cpython':
    # Use the CPython version:
    from .implementations.cpy import *
elif _implementation.name == 'micropython':
    raise NotImplementedError(
        "Unfortunately there is not yet a MicroPython implementation of this "
        "library and it seems rather unlikely that there ever will be.\n"
        "Perhaps you would like to look into adapting the CircuitPython "
        "implementation for this purpose or simply using CircuitPython "
        "to begin with?"
    )
else:
    # Uh oh, we don't support this platform!
    raise NotImplementedError(
        f"This library is not supported for the {_implementation.name} "
        "implementation of Python.\n"
        "We do, however, support CircuitPython and CPython.\n"
        "If you would like to see support for this implementation, please "
        "open an issue at https://github.com/Windham-High-School/CubeServer-api-python/issues/new"
    )
