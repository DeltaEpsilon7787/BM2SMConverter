from rhythm_interface.traits import Declarative, Keyed, RhythmTime, Structural


# Notes
class TapObject(Keyed, RhythmTime):
    position_trait = None


class LNObject(Keyed, RhythmTime):
    start_position_trait = None
    end_position_trait = None


# Headers
class ChartTitle(Declarative):
    title_trait = None


class ChartArtist(Declarative):
    artist_trait = None


class ChartSubtitle(Declarative):
    subtitle_trait = None


class ChartGenre(Declarative):
    genre_trait = None


class ChartCredit(Declarative):
    credit_trait = None


class ChartDifficulty(Declarative):
    abstract_difficulty_trait = None


class ChartBGA(Declarative):
    background_image_trait = None


class ChartBGM(Declarative):
    background_audio_trait = None


# Timing sections
class BPMChange(Structural):
    start_position_trait = None
    bpm_trait = None


class Stop(Structural):
    stop_position_trait = None
    abstract_stop_duration_trait = None
