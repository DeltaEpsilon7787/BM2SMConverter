from rhythm_interface.traits import TraitMeta


# Level 0 object: The most abstract entity possible
# Do not use directly
class RhythmObject(object, metaclass=TraitMeta):
    pass


# Level 1 object: Common traits of regular entities are defined using this
# Not recommended to use directly
class RhythmRowPoint(RhythmObject):
    __traits__ = ['row_position']
    row_position = None


class RhythmColumnPoint(RhythmObject):
    __traits__ = ['column_position']
    column_position = None


class RhythmRowInterval(RhythmObject):
    __traits__ = ['row_interval_start',
                  'row_interval_end']
    row_interval_start = None
    row_interval_end = None


class RhythmColumnInterval(RhythmObject):
    __traits__ = ['column_interval_start',
                  'column_interval_end']
    column_interval_start = None
    column_interval_end = None


class RhythmState(RhythmObject):
    __traits__ = ['state_key',
                  'state_value']
    state_key = None
    state_value = None


class RhythmCommand(RhythmObject):
    __traits__ = ['command']
    command = None


# Level 2+ classes: All custom objects should (hopefully) be defined here
class Banner(RhythmState):
    __traits__ = ['banner']
    banner = None


class Title(RhythmState):
    __traits__ = ['title']
    title = None


class Subtitle(RhythmState):
    __traits__ = ['subtitle']
    subtitle = None


class Artist(RhythmState):
    __traits__ = ['artist']
    artist = None


class Maker(RhythmState):
    __traits__ = ['maker']
    maker = None


class Genre(RhythmState):
    __traits__ = ['genre']
    genre = None


class GenericTap(RhythmRowPoint, RhythmColumnPoint):
    pass


class GenericLN(RhythmRowPoint, RhythmColumnInterval):
    pass


class GenericMine(RhythmRowPoint, RhythmColumnPoint):
    pass


class GenericRoll(RhythmRowPoint, RhythmColumnInterval):
    pass


# Timing
class AbsoluteBPMChange(RhythmColumnPoint):
    __traits__ = ['new_bpm']
    new_bpm = None


class RelativeBPMChange(RhythmColumnPoint):
    __traits__ = ['bpm_multiplier']
    bpm_multiplier = None


class AbsoluteStop(RhythmColumnPoint):
    __traits__ = ['stop_duration']
    stop_duration = None


class RelativeStop(RhythmColumnInterval):
    pass


class TimingSkip(RhythmColumnInterval):
    pass