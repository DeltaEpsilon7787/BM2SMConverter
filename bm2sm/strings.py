class Strings(object):
    # Internal errors
    INVALID_BEAT = "Non-existent beat: {it}"
    INVALID_BEAT_STOP = "Invalid beat stop duration: {it}"
    INVALID_BPM = "Invalid BPM: {it}"
    INVALID_SEGMENT = "Empty/Invalid segment: {it}"
    INVALID_DIFFICULTY = "Unknown difficulty value {arg_value}"
    INVALID_MEASURE = "Non-positive measure: {it}"
    INVALID_MESSAGE = "Less than 2 character long message: {it}"
    INVALID_MS_STOP = "Invalid ms stop duration: {it}"
    INVALID_TIME = "Non-positive time: {it}"
    INVALID_TIME_SIGNATURE = "Time signature cannot be negative: {it}"
    POSITION_OUT_OF_MEASURE = "Position is out of measure"
    SOUND_SAMPLE_NOT_FOUND = "This audio file doesn't exist: {arg_value}"
    SOUND_SAMPLE_FAILED_TO_LOAD = "Audio file couldn't be loaded: {location}"
    TIMING_ALREADY_FROZEN = "{func} may not be called after calling fix() " \
                            "as the object is supposed to stay immutable"
    TIMING_UNCERTAIN_STATE = "{func} from uncertain state"

    # Chart and user input errors
    BEAT_STOP_TOO_SHORT = "A beat stop would last less than 1 ms which cannot be represented without loss: " \
                          "BPM: {bpm}, Length: {length}"
    EMPTY_CHART = "This chart is empty"
    INVALID_FILE_PATH = "{func}: Invalid file path: {arg_value}"
    INVALID_FIRST_HOLD = "First hold has no start"
    INVALID_INPUT_FILE = "{func}: {arg_value} is an invalid value for in_file."
    INVALID_OUTPUT_DIR = "{func}: {arg_value} is an invalid value for out_dir."
    NO_SOUNDS = "There are no sounds"
    NOT_PLAYER_1 = "This chart is not for Player 1"
    UNCERTAIN_AUDIO_FILE = "Chart defines a wav file that either does not exist or there are multiple candidates: " \
                           "{location}"
    UNSUPPORTED_BEAT_STOP = "Negative/Zero beat stop is not supported: {it}"
    UNSUPPORTED_BPM = "Negative/Zero BPM is not supported, BPM: {arg_value}"
    UNSUPPORTED_CONTROL_FLOW = "Control Flow gimmicks are not supported"
    UNSUPPORTED_LNTYPE = "{func}: Unsupported LNTYPE: {arg_value}"
    UNSUPPORTED_MODE = "Unsupported key signature length of {arg_value}, only 4k, 5k, 6k, 7k, 8k are supported"
