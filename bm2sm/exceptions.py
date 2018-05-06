class ConversionError(ValueError):
    pass


class LNTypeUnsupportedError(ConversionError):
    pass


class UnsupportedControlFlowError(ConversionError):
    pass


class NotPlayer1Error(ConversionError):
    pass


class UndecidableAudioFile(ConversionError):
    pass


class StopIsNotDefined(ConversionError):
    pass


class BPMIsNotDefined(ConversionError):
    pass


class FirstHoldHasNoStart(ConversionError):
    pass


class UnsupportedGameMode(ConversionError):
    pass


class UnknownDifficulty(ConversionError):
    pass


class EmptyChart(ConversionError):
    pass


class BeatStopTooShort(ConversionError):
    pass