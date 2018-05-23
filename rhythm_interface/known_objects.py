from rhythm_interface.traits import TraitMeta


# Most VSRG should never utilize this directly anyway
class RhythmObject(object, metaclass=TraitMeta):
    pass


# Abstract stuff
class RhythmRowPoint(RhythmObject):
    __traits__ = ['abstract_row_point_position']
    abstract_row_point_position = None


class RhythmColumnPoint(RhythmObject):
    __traits__ = ['abstract_column_point_position']
    abstract_column_point_position = None


class RhythmRowInterval(RhythmObject):
    __traits__ = ['abstract_row_interval_start_position',
                  'abstract_row_interval_end_position']
    abstract_row_interval_start_position = None
    abstract_row_interval_end_position = None


class RhythmColumnInterval(RhythmObject):
    __traits__ = ['abstract_column_interval_start_position',
                  'abstract_column_interval_end_position']
    abstract_column_interval_start_position = None
    abstract_column_interval_end_position = None


class RhythmState(RhythmObject):
    __traits__ = ['abstract_state_key',
                  'abstract_state_value']
    abstract_state_key = None
    abstract_state_value = None


class RhythmCommand(RhythmObject):
    __traits__ = ['abstract_command']
    abstract_command = None


# Basic meta data stuff
class Banner(RhythmState):
    __traits__ = ['chart_banner']
    chart_banner = None


class Title(RhythmState):
    __traits__ = ['chart_title']
    chart_title = None


class Subtitle(RhythmState):
    __traits__ = ['chart_subtitle']
    chart_subtitle = None


class Artist(RhythmState):
    __traits__ = ['chart_artist']
    chart_artist = None


class Maker(RhythmState):
    __traits__ = ['chart_maker']
    chart_maker = None


class Genre(RhythmState):
    __traits__ = ['chart_genre']
    chart_genre = None
