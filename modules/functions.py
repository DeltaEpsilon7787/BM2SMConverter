import operator
from functools import partial, reduce
from typing import Sequence


def is_non_str_sequence(source):
    """Return True if `source` is a sequence and not a str"""
    return isinstance(source, Sequence) and not isinstance(source, str)


def feed_forward(functions, initial):
    """`initial` value is propagated through a chain of `functions` and the final result is returned"""
    return reduce(lambda value, func: func(value), functions, initial)


base_36_to_dec = partial(int, base=36)
base_16_to_dec = partial(int, base=16)


def identity(v): return v


is_in = partial(partial, operator.contains)


# noinspection PyUnusedLocal
def null_func(*args, **kwargs):
    return True
