from rhythm_interface.traits import TraitMeta


# Most VSRG should never utilize this directly anyway
class RhythmObject(object, metaclass=TraitMeta):
    pass


# Abstract stuff
class RhythmRowPoint(RhythmObject):
    abstract_row_point_position_trait = None


class RhythmColumnPoint(RhythmObject):
    abstract_column_point_position_trait = None


class RhythmRowInterval(RhythmObject):
    abstract_row_interval_start_position_trait = None
    abstract_row_interval_end_position_trait = None


class RhythmColumnInterval(RhythmObject):
    abstract_column_interval_start_position_trait = None
    abstract_column_interval_end_position_trait = None


class RhythmState(RhythmObject):
    abstract_state_key_trait = None
    abstract_state_value_trait = None


class RhythmCommand(RhythmObject):
    abstract_command_trait = None


# Basic meta data stuff
class Banner(RhythmState):
    chart_banner_trait = None


class Title(RhythmState):
    chart_title_trait = None


class Subtitle(RhythmState):
    chart_subtitle_trait = None


class Artist(RhythmState):
    chart_artist_trait = None


class Maker(RhythmState):
    chart_maker_trait = None


class Genre(RhythmState):
    chart_genre_trait = None
