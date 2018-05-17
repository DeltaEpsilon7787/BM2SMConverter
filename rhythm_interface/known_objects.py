from rhythm_interface.traits import AbsoluteTime, Declarative, Keyed, RelativeTime, RhythmTime, Structural


# Notes
class NoteObject(Keyed):
    pass


class TapObject(NoteObject, RhythmTime):
    __additional_init_kwarg_allowed__ = {'tap_time'}
    pass


class LNObject(NoteObject, RhythmTime):
    __additional_init_kwarg_allowed__ = {'LN_start_time', 'LN_end_time'}
    pass


class TapObjectAbsolute(TapObject, AbsoluteTime):
    pass


class TapObjectRelative(TapObject, RelativeTime):
    pass


class LNObjectAbsolute(LNObject, AbsoluteTime):
    pass


class LNObjectRelative(LNObject, RelativeTime):
    pass


# Headers
class ChartTitle(Declarative):
    __additional_init_kwarg_allowed__ = {'title'}
    pass


class ChartArtist(Declarative):
    __additional_init_kwarg_allowed__ = {'artist'}
    pass


class ChartSubtitle(Declarative):
    __additional_init_kwarg_allowed__ = {'subtitle'}
    pass


class ChartGenre(Declarative):
    __additional_init_kwarg_allowed__ = {'genre'}
    pass


class ChartCredit(Declarative):
    __additional_init_kwarg_allowed__ = {'credit'}
    pass


class ChartDifficulty(Declarative):
    __additional_init_kwarg_allowed__ = {'difficulty'}
    pass


class ChartBG(Declarative):
    __additional_init_kwarg_allowed__ = {'bg'}
    pass


class ChartAudio(Declarative):
    __additional_init_kwarg_allowed__ = {'audio'}
    pass


# Timing sections
class BPMChange(Structural):
    __additional_init_kwarg_allowed__ = {'BPM_start_time', 'BPM'}


class BPMChangeAbsolute(BPMChange, AbsoluteTime):
    pass


class BPMChangeRelative(BPMChange, RelativeTime):
    pass


class Stop(Structural):
    __additional_init_kwarg_allowed__ = {'stop_start_time'}


class RelativeStop(Stop):
    __additional_init_kwarg_allowed__ = {'relative_duration'}
