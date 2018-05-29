

# Level 0 classes: The most abstract entity possible
# Do not use directly
class RhythmObject(object):
    pass


class RhythmState(object):
    value = None

    def __init__(self, value):
        self.value = value


class ChartTitle(RhythmState):
    pass


class Subtitle(RhythmState):
    pass


class ChartArtist(RhythmState):
    pass


class ChartBanner(RhythmState):
    pass


class ChartBG(RhythmState):
    pass


class ChartDifficultyName(RhythmState):
    pass


class ChartDifficultyValue(RhythmState):
    pass