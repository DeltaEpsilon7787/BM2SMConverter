import operator
from fractions import Fraction
from itertools import chain
from typing import Callable, List, Tuple

from bm2sm.custom_fake_types import BPM, Beat, BeatStop, ChartPosition, Measure, MsStop, Time, TimeSignature
from bm2sm.exceptions import BeatStopTooShort
from modules.decorators import transform_args, transform_return
from modules.fake_types import NonNegativeInt, PositiveFraction


class TimingSectionManager(object):
    """Manager for all manners of timing changes"""
    _time_signature_changes = ...  # type: List[Tuple[NonNegativeInt, TimeSignature]]
    _ms_stops = ...  # type: List[Tuple[ChartPosition, MsStop]]
    _position_to_time = ...  # type: Callable[ChartPosition, Time]
    _fixed = ...  # type: bool
    _bpm_changes = ...  # type: List[Tuple[ChartPosition, BPM]]

    def __init__(self):
        self._bpm_changes = []
        self._fixed = False
        self._position_to_time = None
        self._ms_stops = []
        self._time_signature_changes = []

    @transform_args(..., ChartPosition, BeatStop)
    def add_beat_stop(self, measure, stop_duration):
        # Stepmania does not have real beat stops so we'll have to approximate by adding a close enough ms stop.
        #   BPM changes cannot be added as they will change the topology of the chart.
        stop_duration = Fraction(stop_duration, 192)
        closest_bpm = [v for v in self._bpm_changes if v[0] <= measure][-1][1]
        duration_real = stop_duration * Fraction(240000, closest_bpm)
        duration_usable = round(duration_real)

        if duration_usable <= 0:
            raise BeatStopTooShort('There is a beat stop that is shorter than 1 ms')
        self.add_ms_stop(measure, duration_usable)

    @transform_args(..., Measure, MsStop)
    def add_ms_stop(self, measure, stop_duration):
        self._ms_stops.append((measure, Fraction(stop_duration, 1000)))

    @transform_args(..., Measure, BPM)
    def add_bpm_change(self, measure, new_bpm):
        self._bpm_changes.append((measure, new_bpm))

    @transform_args(..., Measure, TimeSignature)
    def add_time_signature_change(self, measure, value):
        temp = dict(self._time_signature_changes)
        temp[NonNegativeInt(measure)] = PositiveFraction(value)
        self._time_signature_changes = list(temp.items())
        self._time_signature_changes.sort(key=operator.itemgetter(0))

    # This must be called after topology of the notefield has been defined.
    # This will make this object functionally immutable.

    def fix(self):
        all_lists = [self._bpm_changes, self._ms_stops]

        for lst in all_lists:
            beats_present = set()
            result = []
            for beat, value in reversed(lst):
                if beat not in beats_present:
                    beats_present.add(beat)
                    result.append((beat, value))
            result = sorted(result, key=operator.itemgetter(0))
            lst.clear()
            lst += result

        def make_bpm_func(period, bpm):
            fr, to = period
            coefficient = Fraction(240, bpm)

            def bpm_func(position):
                position = max(fr, min(to, position))
                delta = position - fr
                return delta * coefficient

            return bpm_func

        def make_ms_stop_func(stop_start, stop_duration):
            def ms_stop_func(position):
                return stop_duration if position > stop_start else 0

            return ms_stop_func

        start_points, new_bpm = zip(*self._bpm_changes)
        start_points = tuple(chain(start_points, (9e4000,)))
        ranges = zip(start_points[:-1], start_points[1:])
        steps = zip(ranges, new_bpm)

        bpm_funcs = [make_bpm_func(*T) for T in steps]
        ms_stop_funcs = [make_ms_stop_func(*T) for T in self._ms_stops]

        full_chain = bpm_funcs + ms_stop_funcs

        @transform_args(ChartPosition)
        @transform_return(Time)
        def calculate_time_by_position(position):
            return sum(map(lambda v: v(position), full_chain))

        self._position_to_time = calculate_time_by_position
        self._fixed = True


    def _split_fraction_for_string(self, fraction):
        integer_part = fraction.numerator // fraction.denominator
        fractional_part = fraction.numerator % fraction.denominator
        assert 1000 % fraction.denominator == 0
        fractional_part *= 1000 // fraction.denominator

        return integer_part, fractional_part


    @property
    def position_to_time(self):
        return self._position_to_time

    @property
    def bpm_string(self):
        return ",".join(
            '{}.{:03g}={}.{:03g}'.format(
                *self._split_fraction_for_string(Beat(4 * measure)),
                *self._split_fraction_for_string(value))
            for measure, value in self._bpm_changes
        )

    @property
    def bpm_dict(self):
        return dict(self._bpm_changes)

    @property
    def bpm_list(self):
        return list(self._bpm_changes)

    @property
    def is_fixed(self):
        return self._fixed

    @property
    def is_not_fixed(self):
        return not self.is_fixed

    @property
    def ms_stops_string(self):
        return ",".join(
            '{}.{:03g}={}.{:03g}'.format(
                *self._split_fraction_for_string(Beat(4 * measure)),
                *self._split_fraction_for_string(value))
            for measure, value in self._ms_stops
        )

    @property
    def ms_stops_dict(self):
        return dict(self._ms_stops)

    @property
    def ms_stops_list(self):
        return list(self._ms_stops)

    @property
    def time_sgn_string(self):
        return ",".join(
            '{}.{:03g}={}={}'.format(*self._split_fraction_for_string(Beat(4 * measure)),
                                     sgn.numerator,
                                     sgn.denominator)
            for measure, sgn in self._time_signature_changes
        )

    @property
    def time_sgn_dict(self):
        return dict(self._time_signature_changes)

    @property
    def time_sgn_list(self):
        return list(self._time_signature_changes)
