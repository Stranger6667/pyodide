from collections import namedtuple
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parents[2]))

from pyodide_build.pywasmcross import handle_command  # noqa: E402


def _args_wrapper(func):
    """Convert function to take as input / return a string instead of a
    list of arguments

    Also sets pretend=True
    """
    def _inner(line, *pargs):
        args = line.split()
        res = func(args, *pargs, pretend=True)
        if hasattr(res, '__len__'):
            return ' '.join(res)
        else:
            return res
    return _inner


handle_command_wrap = _args_wrapper(handle_command)
# TODO: add f2c here


def test_handle_command():
    Args = namedtuple('args', ['cflags', 'ldflags'])
    args = Args(cflags='', ldflags='')
    assert handle_command_wrap('gcc -print-multiarch', args) is None
    assert handle_command_wrap('gcc test.c', args) == 'emcc test.c'
    assert handle_command_wrap('gcc -shared -c test.o -o test.so', args) == \
        'emcc -shared -c test.bc -o test.wasm'

    # check ldflags injection
    args = Args(cflags='', ldflags='-lm')
    assert handle_command_wrap('gcc -shared -c test.o -o test.so', args) == \
        'emcc -lm -shared -c test.bc -o test.wasm'

    # compilation checks in numpy
    assert handle_command_wrap('gcc /usr/file.c', args) is None
