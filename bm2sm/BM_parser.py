import operator
from fractions import Fraction
from glob import glob, escape
from os import path
from re import findall, match
from shutil import copy2

from chardet import detect as char_detect

from bm2sm.OGG_converter import OGGConverter
from bm2sm.SM_converter import SMChartConverter
from bm2sm.custom_fake_types import BPM, Beat, MsStop, Segment
from bm2sm.data_structures import Datum, NotefieldObject, Sound, SoundSample
from bm2sm.definitions import Keys, Representations, standard_tqdm
from bm2sm.exceptions import BPMIsNotDefined, FirstHoldHasNoStart, LNTypeUnsupportedError, NotPlayer1Error, \
    StopIsNotDefined, UndecidableAudioFile, UnsupportedControlFlowError
from bm2sm.timing_manager import TimingSectionManager
from modules import null_func
from modules.decorators import transform_args
from modules.fake_types import CastableToInt, PositiveInt
from modules.functions import base_16_to_dec, is_non_str_sequence


class BMChartParser(object):
    """A class where all the heavy lifting of parsing BM files is happening."""

    def __init__(self, in_file, out_dir, keys, load_sounds):
        self._extended_BPM_definitions = {}
        self._extended_stop_definitions = {}
        self._wav_files_definitions = {}

        self._LN_objects = set()
        self._LN_opened = {}
        self._LN_type = 1

        self.BM_file_name = path.splitext(path.basename(in_file))[0]
        self.BM_file_dir = path.dirname(in_file)
        self.BM_file_path = in_file

        self.OGG_converter = OGGConverter(self)
        self.OGG_file_name = self.BM_file_name + '.ogg'
        self.OGG_file_dir = out_dir or self.BM_file_dir
        self.OGG_file_path = path.join(self.OGG_file_dir, self.OGG_file_name)

        self.SM_converter = SMChartConverter(self, keys)
        self.SM_file_name = self.BM_file_name + '.sm'
        self.SM_file_dir = out_dir or self.BM_file_dir
        self.SM_file_path = path.join(self.SM_file_dir, self.SM_file_name)

        self._affected_files = set()

        self._dynamic_data = []
        self._static_data = []

        self.timing_manager = TimingSectionManager()

        self._add_object = self.SM_converter.objects.append

        # Reference: #BPM
        #   When this command is omitted, 130 is applied as a default.
        #   But if it is a decent musical score, #BPM should not omit.
        self._set_initial_bpm(130)

        # Some hooks
        copying_needed = not path.samefile(self.BM_file_dir, self.SM_file_dir)
        if not copying_needed:
            self.add_file_to_copy = null_func
            self.copy_files = null_func

        if not load_sounds:
            self._add_sound = null_func
            self._define_wav = null_func

        self._perform_static_reading()
        self._process_static_data()
        self._process_dynamic_data()

    def _add_bpm_change(self, datum: Datum):
        try:
            bpm = base_16_to_dec(datum.value)
        except ValueError:
            print('Invalid segment for BPM')
            raise
        self.timing_manager.add_bpm_change(datum.global_position, bpm)

    def _add_beat_stop(self, datum: Datum):
        if datum.value not in self._extended_stop_definitions:
            raise StopIsNotDefined(datum.value)
        self.timing_manager.add_beat_stop(datum.global_position,
                                          self._extended_stop_definitions[datum.value])

    def _add_extended_bpm_change(self, datum: Datum):
        if datum.value not in self._extended_BPM_definitions:
            raise BPMIsNotDefined(datum.value)
        self.timing_manager.add_bpm_change(datum.global_position, self._extended_BPM_definitions[datum.value])

    @transform_args(..., Segment, **{
        '@1': 'This LNOBJ is invalid'
    })
    def _add_ln_object(self, value):
        self._LN_objects.add(value)

    @transform_args(..., MsStop, PositiveInt, PositiveInt, **{
        '@2': 'Invalid STP definition',
        '@3': 'Invalid STP definition'
    })
    def _add_ms_stop(self, duration, measure, measure_part):
        measure_part = Fraction(measure_part, 1000)
        beat = Beat(measure + measure_part)
        self.timing_manager.add_ms_stop(beat, duration)

    def _add_sound(self, datum: Datum):
        if datum.value not in self._wav_files_definitions:
            return
        sound = self._wav_files_definitions[datum.value].segment
        if not sound:
            return
        time = self.timing_manager.position_to_time(datum.global_position)
        self.OGG_converter.sounds.append(Sound(datum.value,
                                               sound,
                                               time))

    def _add_time_signature_change(self, datum_with_perks):
        measure = datum_with_perks.initial_measure
        measure_length = datum_with_perks.time_signature

        self.timing_manager.add_time_signature_change(measure, measure_length)

    @transform_args(..., CastableToInt, **{
        '@1': 'Cannot parse the expression of PLAYER'
    })
    def _assert_correct_player(self, player):
        if player != 1:
            raise NotPlayer1Error(player)

    @transform_args(..., BPM, Segment, **{
        '@1': 'Invalid BPM definition'
    })
    def _define_extended_bpm(self, bpm, bpm_id):
        self._extended_BPM_definitions[bpm_id] = bpm

    @transform_args(..., MsStop, Segment, **{
        '@1': 'Invalid STOP definition'
    })
    def _define_stop(self, dur, stop_id):
        self._extended_stop_definitions[stop_id] = dur

    @transform_args(..., ..., Segment)
    def _define_wav(self, value, wav_id):
        header = path.dirname(self.BM_file_path)
        filename = path.splitext(path.basename(value))[0]
        file_path = escape(path.join(header, filename))
        candidates = glob(file_path + '.*')

        if len(candidates) != 1:
            raise UndecidableAudioFile(value)

        self._wav_files_definitions[wav_id] = SoundSample(candidates[0])

    def _feed_message(self, message):
        channel_regex = r'\s*#(\d{3})(\w{2}):(\w{2,})\s*'
        time_signature_regex = r'\s*#(\d{3})02:([\d\.]+)\s*'  # Because we are so special and unique, aren't we
        header_regex = r'\s*#(\w+)\s+([^\n\r]+)\s*'
        stp_regex = r'\s*#STP\s+(\d{3})\.(\d{3})\s+(\d+)\s*'  # Has a special syntax because why wouldn't it

        defined_channels = ('01', '02', '03', '08', '09',
                            '11', '12', '13', '14', '15', '16', '18', '19',
                            '31', '32', '33', '34', '35', '36', '38', '39',
                            '51', '52', '53', '54', '55', '56', '58', '59',
                            'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D8', 'D9')

        if match(time_signature_regex, message):
            measure, value = findall(time_signature_regex, message)[0]
            measure = int(measure)
            value = Fraction(value)

            datum_with_perks = Datum('00', measure, 0, 192)
            datum_with_perks.time_signature = value

            self._dynamic_data.append((
                measure,
                '02',
                datum_with_perks
            ))

        elif match(stp_regex, message):
            measure, measure_part, duration = findall(stp_regex, message)[0]
            self._static_data.append(('STP {}.{}'.format(measure, measure_part), duration))

        elif match(channel_regex, message):
            measure, channel, data = findall(channel_regex, message)[0]
            channel = channel.upper()
            if channel not in defined_channels:
                return
            measure = int(measure)
            data = Datum.from_message(data, measure)

            for datum in data:
                self._dynamic_data.append((measure, channel, datum))

        elif match(header_regex, message):
            header, value = findall(header_regex, message)[0]
            self._static_data.append((header, value))

    def _make_key_adder(self, key):
        # noinspection PyUnusedLocal
        def key_adder(datum):
            new_object = ...
            val = datum.value
            if val in self._LN_objects:
                # LNOBJ stuff
                if len(self.SM_converter.objects) == 0:
                    raise FirstHoldHasNoStart
                last_tap_note = sorted((T
                                        for T in self.SM_converter.objects
                                        if T.key == key
                                        if T.symbol == Representations.TAP),
                                       key=operator.attrgetter('position'))[-1]
                last_tap_note.symbol = Representations.LN_START
                new_object = NotefieldObject(datum.global_position,
                                             key,
                                             Representations.LN_END)
            else:
                new_object = NotefieldObject(datum.global_position,
                                             key,
                                             Representations.TAP)
                self._add_sound(datum)
            self._add_object(new_object)

        return key_adder

    def _make_ln_adder(self, key):
        if key not in self._LN_opened:
            self._LN_opened[key] = False

        # noinspection PyUnusedLocal,PyUnusedLocal
        def ln_adder(datum):
            if self._LN_type == 1:
                new_object = None
                if not self._LN_opened[key]:
                    new_object = NotefieldObject(datum.global_position, key, Representations.LN_START)
                    self._add_sound(datum)
                    self._LN_opened[key] = True
                else:
                    new_object = NotefieldObject(datum.global_position, key, Representations.LN_END)
                    self._LN_opened[key] = False
            elif self._LN_type == 2:
                # MGQ
                new_object = None
                if not self._LN_opened[key]:
                    new_object = NotefieldObject(datum.global_position, key, Representations.LN_START)
                    self._add_sound(datum)
                    self._LN_opened[key] = True
                else:
                    if datum.value != '00':
                        return
                    new_object = NotefieldObject(datum.global_position, key, Representations.LN_END)
                    self._LN_opened[key] = False
            else:
                return
            self._add_object(new_object)

        return ln_adder

    def _make_mine_adder(self, key):
        def mine_adder(datum):
            new_object = NotefieldObject(datum.global_position,
                                         key,
                                         Representations.MINE)
            self._add_object(new_object)

        return mine_adder

    # Previous algorithm was naive and, while okay for most applications, it would become
    #  a massive performance drain for any chart that uses lots of time signature changes
    #    which is not that uncommon
    # Basically previous algorithm was a O(2n^2) on.
    # This algorithm is expected to perform in O(n)

    # The algorithm exploits presence of order for datums and time changes
    #   Which allows to create a concurrent environment as follows.
    # noinspection PyPropertyAccess
    def _offset_dynamic_data(self):
        ordered_datums = sorted((T[2] for T in self._dynamic_data),
                                key=operator.attrgetter('initial_measure'))
        ordered_time_sgn = self.timing_manager.time_sgn_list

        if len(ordered_time_sgn) == 0:
            return

        current_shift = 0
        new_shift = 0
        current_time_sgn = ordered_time_sgn.pop(0)
        changing_displacement = True

        with standard_tqdm(iterable=ordered_datums, desc='Displacing rows') as progress_ordered_datum:
            for datum in progress_ordered_datum:
                displacement_measure, displacement_amount = current_time_sgn

                while datum.initial_measure > displacement_measure:
                    if len(ordered_time_sgn) == 0:
                        displacement_measure, displacement_amount = 9e4000, 9e4000
                    else:
                        current_time_sgn = ordered_time_sgn.pop(0)
                        displacement_measure, displacement_amount = current_time_sgn
                        current_shift += new_shift
                        new_shift = displacement_amount - 1
                        changing_displacement = False

                if datum.initial_measure < displacement_measure:
                    changing_displacement = False
                    datum.global_position += current_shift

                if datum.initial_measure == displacement_measure:
                    local_position = datum.initial_position - datum.initial_measure
                    new_local_position = local_position * displacement_amount
                    displacement = new_local_position - local_position
                    datum.global_position += displacement
                    datum.global_position += current_shift
                    if not changing_displacement:
                        new_shift = displacement_amount - 1
                        changing_displacement = True

    def _parse_implicit_subtitle(self, subtitle):
        keywords_to_difficulty = {
            1: ("EASY", "BEGINNER", "LIGHT", "SIMPLE", "[B]", "(B)"),
            2: ("NORMAL", "STANDARD", "[N]", "(N)"),
            3: ("HYPER", "HARD", "EXTEND", "[H]", "(H)"),
            4: ("MANIAC", "EXTRA", "EX"),
            5: ("INSANE", "ANOTHER", "PLUS", "[A]", "(A)")
        }

        subtitle = subtitle.upper()
        for probable_diff in keywords_to_difficulty:
            for probable_keyword in keywords_to_difficulty[probable_diff]:
                if probable_keyword in subtitle:
                    self.SM_converter.set_difficulty(probable_diff)

    def _puke_from_gimmicks(self, _=0):
        raise UnsupportedControlFlowError

    @transform_args(..., BPM, **{
        '@1': 'Invalid initial BPM'
    })
    def _set_initial_bpm(self, value):
        self.timing_manager.add_bpm_change(0, value)

    @transform_args(..., CastableToInt, **{
        '@1': 'Invalid LNType'
    })
    def _set_ln_type(self, value):
        if value not in (1, 2):
            raise LNTypeUnsupportedError(value)
        self._LN_type = value

    def copy_files(self):
        output_dir = path.dirname(self.SM_file_path)

        if len(self._affected_files) == 0:
            return

        with standard_tqdm(iterable=self._affected_files, desc="Copying files into new directory") as progress_affected_files:
            for file_path in progress_affected_files:
                file_name = path.split(file_path)[1]
                output_file = path.join(output_dir, file_name)
                if path.exists(output_file):
                    return
                copy2(file_path, output_file)

    def _perform_static_reading(self):
        try:
            with open(self.BM_file_path, 'rb') as in_file:
                encoding = char_detect(in_file.read())['encoding']

            with open(self.BM_file_path, 'r', encoding=encoding) as in_file:
                data = in_file.readlines()
        except IOError:
            print('Error occurred when opening BM chart')
            raise

        with standard_tqdm(iterable=data, desc='Performing static reading') as progress_data:
            for datum in progress_data:
                self._feed_message(datum)

    def _process_dynamic_data(self):
        self._dynamic_data = sorted(self._dynamic_data, key=lambda v: v[0])

        lengths = {
            '02': self._add_time_signature_change
        }

        slopes = {
            '03': self._add_bpm_change,
            '08': self._add_extended_bpm_change
        }

        discontinuities = {
            '09': self._add_beat_stop
        }

        content = {
            '01': self._add_sound,
            '11': self._make_key_adder(Keys.KEY_1),
            '12': self._make_key_adder(Keys.KEY_2),
            '13': self._make_key_adder(Keys.KEY_3),
            '14': self._make_key_adder(Keys.KEY_4),
            '15': self._make_key_adder(Keys.KEY_5),
            '18': self._make_key_adder(Keys.KEY_6),
            '19': self._make_key_adder(Keys.KEY_7),
            '16': self._make_key_adder(Keys.SCRATCH),
            '31': self._add_sound,
            '32': self._add_sound,
            '33': self._add_sound,
            '34': self._add_sound,
            '35': self._add_sound,
            '38': self._add_sound,
            '39': self._add_sound,
            '51': self._make_ln_adder(Keys.KEY_1),
            '52': self._make_ln_adder(Keys.KEY_2),
            '53': self._make_ln_adder(Keys.KEY_3),
            '54': self._make_ln_adder(Keys.KEY_4),
            '55': self._make_ln_adder(Keys.KEY_5),
            '58': self._make_ln_adder(Keys.KEY_6),
            '59': self._make_ln_adder(Keys.KEY_7),
            '56': self._make_ln_adder(Keys.SCRATCH),
            'D1': self._make_mine_adder(Keys.KEY_1),
            'D2': self._make_mine_adder(Keys.KEY_2),
            'D3': self._make_mine_adder(Keys.KEY_3),
            'D4': self._make_mine_adder(Keys.KEY_4),
            'D5': self._make_mine_adder(Keys.KEY_5),
            'D8': self._make_mine_adder(Keys.KEY_6),
            'D9': self._make_mine_adder(Keys.KEY_7),
            'D6': self._make_mine_adder(Keys.SCRATCH)
        }

        def do_scan(simple_deciders, message):
            amount = 0
            filtered = []
            for measure, channel, datum in self._dynamic_data:
                if channel in simple_deciders:
                    filtered.append((measure, channel, datum))
                    amount += 1
            if amount == 0:
                return

            with standard_tqdm(iterable=filtered, desc=message, total=amount) as progress_dynamic_data:
                for measure, channel, datum in progress_dynamic_data:
                    if channel in simple_deciders:
                        simple_deciders[channel](datum)

        # All of this is used to map beats to time on the notefield
        do_scan(lengths, 'Processing time signature changes')
        self._offset_dynamic_data()
        do_scan(slopes, 'Processing BPM changes')
        do_scan(discontinuities, 'Processing stops')
        self.timing_manager.fix()

        # And then add objects to the notefield
        do_scan(content, 'Parsing objects')

    # noinspection SpellCheckingInspection
    def _process_static_data(self):
        simple_deciders = {
            'PLAYER': self._assert_correct_player,
            'TITLE': self.SM_converter.make_setter('title'),
            'SUBTITLE': self._parse_implicit_subtitle,
            'ARTIST': self.SM_converter.make_setter('artist'),
            'BPM': self._set_initial_bpm,
            'DIFFICULTY': self.SM_converter.set_difficulty,
            'LNTYPE': self._set_ln_type,
            'LNOBJ': self._add_ln_object,
            'STAGEFILE': self.SM_converter.make_file_setter('bg'),
            'BANNER': self.SM_converter.make_file_setter('banner'),
            'END IF': self._puke_from_gimmicks,
            'ELSE': self._puke_from_gimmicks,
            'ENDRANDOM': self._puke_from_gimmicks,
            'SKIP': self._puke_from_gimmicks,
            'DEF': self._puke_from_gimmicks,
            'ENDSW': self._puke_from_gimmicks,
            'RANDOM': self._puke_from_gimmicks,
            'IF': self._puke_from_gimmicks,
            'RONDAM': self._puke_from_gimmicks,
            'SETRANDOM': self._puke_from_gimmicks,
            'ELSEIF': self._puke_from_gimmicks,
            'SWITCH': self._puke_from_gimmicks,
            'CASE': self._puke_from_gimmicks,
        }

        advanced_deciders = {
            r'STP (\d{3})\.(\d{3})': self._add_ms_stop,
            r'BPM([0-9a-fA-F]{2})': self._define_extended_bpm,
            r'EXBPM([0-9a-fA-F]{2})': self._define_extended_bpm,
            r'STOP([0-9a-zA-Z]{2})': self._define_stop,
            r'WAV([0-9a-zA-Z]{2})': self._define_wav
        }

        with standard_tqdm(iterable=self._static_data, desc='Processing static data') as progress_static_data:
            for header, value in progress_static_data:
                header = header.upper()
                if header in simple_deciders:
                    simple_deciders[header](value)

                for candidate in advanced_deciders:
                    if match(candidate, header):
                        additional_data = findall(candidate, header)[0]
                        if is_non_str_sequence(additional_data):
                            advanced_deciders[candidate](value, *additional_data)
                        else:
                            advanced_deciders[candidate](value, additional_data)

    def add_file_to_copy(self, file_path):
        file_path = (file_path
                     if path.dirname(file_path) == self.BM_file_dir
                     else path.join(self.BM_file_dir, file_path))
        self._affected_files.add(file_path)
