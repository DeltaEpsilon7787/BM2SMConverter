import sys

from tqdm import tqdm

DEFAULT_FRAME_RATE = 44100


def standard_tqdm(*args, **kwargs):
    return tqdm(*args,
                bar_format='{desc:>36} @ {percentage:>3.0f}% [{remaining:>5}] [{n:>6}/{total:>6}]|{bar}|',
                file=sys.stdout,  # Not sure why tqdm outputs to stderr by default
                **kwargs)


class Keys(object):
    KEY_1 = 0
    KEY_2 = 1
    KEY_3 = 2
    KEY_4 = 3
    KEY_5 = 4
    KEY_6 = 5
    KEY_7 = 6
    SCRATCH = 7
    NONE = 8

    KEYS = {
        '1': 'KEY_1',
        '2': 'KEY_2',
        '3': 'KEY_3',
        '4': 'KEY_4',
        '5': 'KEY_5',
        '6': 'KEY_6',
        '7': 'KEY_7',
        'S': 'SCRATCH',
        'X': 'NONE'
    }

    META = {
        4: 'dance-single',
        5: 'pump-single',
        6: 'dance-solo',
        7: 'kb7-single',
        8: 'dance-double',
        10: 'pump-double'
    }


class Representations(object):
    NOTHING = '0'
    TAP = '1'
    LN_START = '2'
    LN_END = '3'
    MINE = 'M'
