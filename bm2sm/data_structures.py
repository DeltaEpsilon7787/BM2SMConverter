from fractions import Fraction
from itertools import count as iter_count

from pydub import AudioSegment

from bm2sm.definitions import DEFAULT_FRAME_RATE, Keys
from modules.decorators import transform_args, transform_return
from modules.fake_types import CastableToInt, NonNegativeInt, PositiveInt
from .custom_fake_types import Character, ChartPosition, Measure, Message, Segment, Time


class Datum(object):
    """Basic class representing a channel message from BM files."""
    _initial_measure = ...  # type: Measure
    _id = ...  # type: int
    FREE_ID = 0  # type: int

    @transform_args(..., Segment, Measure, ChartPosition, PositiveInt)
    def __init__(self, value, measure, position, measure_split):
        assert position < measure_split

        self.value = value
        self._id = self.FREE_ID
        self._initial_measure = measure
        self._initial_position = self.initial_measure + Fraction(position, measure_split)

        self._global_position = self.initial_position

        Datum.FREE_ID += 1

    @classmethod
    @transform_args(..., Message, Measure)
    def from_message(cls, message, measure):
        pairs = [''.join(T) for T in zip(message[::2], message[1::2])]

        measure_split = len(pairs)
        enumerated_pairs = zip(iter_count(), pairs)

        result = [
            cls(datum, measure, position, measure_split)
            for position, datum in enumerated_pairs
            if datum != '00'
        ]

        return result

    @property
    def global_position(self):
        return self._global_position

    @global_position.setter
    def global_position(self, value: ChartPosition):
        value = ChartPosition(value)
        self._global_position = value

    @property
    def initial_measure(self):
        return self._initial_measure

    @property
    def initial_position(self):
        return self._initial_position


class NotefieldObject(object):
    """Basic object representing an object on a notefield."""
    position = ...  # type: ChartPosition
    measure = ...  # type: NonNegativeInt
    key = ...  # type: CastableToInt
    symbol = ...  # type: Character

    @transform_args(..., Measure, CastableToInt, Character)
    def __init__(self, position, key, symbol):
        assert key in Keys.__dict__.values()
        self.position = position
        self.measure = position.numerator // position.denominator
        self.key = key
        self.symbol = symbol


class Sound(object):
    """Basic object representing a sound in the audio file."""
    _id = ...  # type: Segment
    sound = ...  # type: AudioSegment
    _time = ...  # type: Time

    @transform_args(..., Segment, ..., Time)
    def __init__(self, wav_id, sound, time):
        # `id` ended up unused after rewriting audio file baking.
        #   It was used to group sounds in layers and simulate sounds being cutoff
        #     as described in the reference
        assert sound

        self._id = wav_id
        self.sound = sound

        if self.sound.frame_rate != DEFAULT_FRAME_RATE:
            self.sound = self.sound.set_frame_rate(DEFAULT_FRAME_RATE)

        self._time = Time(1000 * time)

    @property
    @transform_return(Time)
    def start_time_ms(self):
        return self._time

    @property
    @transform_return(NonNegativeInt)
    def start_time_frames(self):
        return Fraction(DEFAULT_FRAME_RATE, 1000) * self.start_time_ms

    @property
    @transform_return(Time)
    def duration_ms(self):
        return 1000 * Fraction(self.duration_frames, self.sound.frame_rate)

    @property
    @transform_return(NonNegativeInt)
    def duration_frames(self):
        return int(self.sound.frame_count())

    @property
    @transform_return(Time)
    def end_time_ms(self):
        return self.duration_ms + self.start_time_ms

    @property
    @transform_return(NonNegativeInt)
    def end_time_frames(self):
        return self.start_time_frames + self.duration_frames


class SoundSample(object):
    """Basic object representing a loaded keynote sound."""

    _location = ...  # type: str
    _segment = ...  # type: AudioSegment

    def __init__(self, location):
        self._location = location
        self._segment = None

    @property
    def segment(self):
        if self._segment:
            return self._segment
        self._segment = AudioSegment.from_file(self._location)
        assert self._segment
        return self._segment
