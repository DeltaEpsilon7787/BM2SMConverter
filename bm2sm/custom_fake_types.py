"""A family of fake types that implicitly cast given value to caster's type"""

import operator
from fractions import Fraction
from functools import partial

from bm2sm.definitions import DEFAULT_FRAME_RATE
from modules.fake_types import Castable, NonNegativeFraction, NonNegativeInt, PositiveFraction
from modules.functions import feed_forward
from .strings import Strings


def discretizer(precision):
    """Create a discretizer function that attempts to find the closest multiple of `precision` for argument."""
    assert precision > 0

    def discretize(v):
        first_candidate = v // precision * precision
        second_candidate = first_candidate - precision
        third_candidate = first_candidate + precision

        de1 = abs(v - first_candidate)
        de2 = abs(v - second_candidate)
        de3 = abs(v - third_candidate)

        # Floating point memes, hooray
        if de1 <= de2 and de1 <= de3:
            return first_candidate
        if de2 <= de1 and de2 <= de3:
            return second_candidate
        if de3 <= de1 and de3 <= de2:
            return third_candidate

    return discretize


bpm_discretizer = discretizer(Fraction(1, 1000))
# 0.001 in SM files is misleading, the actual accuracy seems to be 1/48.
# Yet you still have to write in thousandths
beat_discretizer = partial(
    feed_forward,
    (
        discretizer(Fraction(1, 48)),
        discretizer(Fraction(1, 1000))
    )
)
chart_position_discretizer = discretizer(Fraction(1, 192))  # Decoupled from beats
ms_stop_discretizer = discretizer(Fraction(1, 1000))
sound_discretizer = discretizer(Fraction(1, DEFAULT_FRAME_RATE))


class Beat(NonNegativeFraction):
    cast_fail_message = Strings.INVALID_BEAT
    discretizer = beat_discretizer


class BPM(PositiveFraction):
    cast_fail_message = Strings.INVALID_BPM
    discretizer = bpm_discretizer


class ChartPosition(NonNegativeFraction):
    cast_fail_message = Strings.INVALID_MEASURE
    discretizer = chart_position_discretizer


class Measure(NonNegativeFraction):
    cast_fail_message = Strings.INVALID_MEASURE


class Message(Castable, str):
    cast_fail_message = Strings.INVALID_MESSAGE
    caster = partial(feed_forward, (str, operator.methodcaller('upper')))
    post_check = partial(feed_forward, (len, partial(operator.le, 2)))


class Character(Castable, str):
    caster = str
    post_check = partial(feed_forward, (len, partial(operator.eq, 1)))


class Segment(Castable, str):
    """A type used to represent two character strings derived from messages"""
    cast_fail_message = Strings.INVALID_SEGMENT
    caster = partial(feed_forward, (str, operator.methodcaller('upper')))
    post_check = partial(feed_forward, (len, partial(operator.eq, 2)))


class Time(NonNegativeFraction):
    cast_fail_message = Strings.INVALID_TIME
    discretizer = sound_discretizer


class TimeSignature(PositiveFraction):
    cast_fail_message = Strings.INVALID_TIME_SIGNATURE


class MsStop(Time):
    cast_fail_message = Strings.INVALID_MS_STOP


class BeatStop(NonNegativeInt):
    cast_fail_message = Strings.UNSUPPORTED_BEAT_STOP
