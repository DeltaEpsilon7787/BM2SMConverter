import operator
from functools import partial
from typing import Any, Dict, List

from tqdm import tqdm

from bm2sm.data_structures import NotefieldObject
from bm2sm.definitions import Keys, Representations, standard_tqdm
from bm2sm.exceptions import EmptyChart, UnknownDifficulty, UnsupportedGameMode
from modules.additional_functions import lcm
from modules.decorators import transform_args
from modules.fake_types import CastableToInt, NonNegativeInt


class SMChartConverter(object):
    """A class composing the SM chart."""
    _SM_format = """#TITLE:{title};
#SUBTITLE:{subtitle};
#ARTIST:{artist};
#CREDIT:{credit};
#MUSIC:{audio_name};
#SELECTABLE:YES;
#BANNER:{banner};
#BACKGROUND:{bg};
#GENRE:{genre}
#CDTITLE:;
#OFFSET:0.0000000;
#BPMS:{BPM_changes};
#STOPS:{stops};
#NOTES:
{game_mode}:
:
{difficulty_name}:
{difficulty}:
0.000,0.000,0.000,0.000,0.000:
{measures}
;"""
    objects = ...  # type: List[NotefieldObject]
    _parent = ...  # type: 'BMChartParser'
    _meta_data = ...  # type: Dict[str, Any]

    def __init__(self, parent, keys):
        self._meta_data = {
            'artist': "Unknown",
            'bg': '',
            'banner': '',
            'credit': '',
            'difficulty': 5,
            'difficulty_name': "Edit",
            'genre': '',
            'subtitle': '',
            'title': "Unknown",
        }
        self.objects = []
        self._parent = parent

        try:
            self._meta_data['game_mode'] = Keys.META[len(keys)]
        except KeyError:
            raise UnsupportedGameMode

        self.keys = [
            getattr(Keys, Keys.KEYS[key])
            for key in keys
        ]

    def compose_chart(self):
        if len(self.objects) == 0:
            raise EmptyChart
        self.objects.sort(key=operator.attrgetter('position'))

        measure_splits = {}

        with standard_tqdm(iterable=self.objects, desc='Composing SM chart manifold') as progress_objects:
            for obj in progress_objects:
                measure = obj.measure
                if measure not in measure_splits:
                    measure_splits[measure] = 4
                cur_split = measure_splits[measure]
                measure_splits[measure] = lcm(cur_split, obj.position.denominator)

        amount_of_measures = max(measure_splits) + 1
        measures = []

        with standard_tqdm(range(amount_of_measures), desc='Filling SM chart with 0') as progress_measures:
            for measure_num in progress_measures:
                length = measure_splits.get(NonNegativeInt(measure_num), 4)
                measures.append(
                    [
                        [
                            Representations.NOTHING
                            for _ in range(len(self.keys))
                        ]
                        for _ in range(length)
                    ]
                )

        with standard_tqdm(iterable=self.objects, desc='Injecting objects into SM chart') as progress_objects:
            for obj in progress_objects:
                measure_split = measure_splits[obj.measure]
                local_position = obj.position.numerator % obj.position.denominator
                scaled_position = local_position * (measure_split //
                                                    obj.position.denominator)

                if obj.key not in self.keys:
                    continue
                relative_position = self.keys.index(obj.key)
                this_measure = measures[obj.measure]

                this_measure[scaled_position][relative_position] = obj.symbol

        row_template = "{}" * len(self.keys)
        notes = "\n,\n".join(
            "\n".join(
                row_template.format(*row)
                for row in measure
            )
            for measure in measures
        )

        audio_out_file = self._parent.OGG_file_name
        result = self._SM_format.format(**{
            **self._meta_data,
            'BPM_changes': self._parent.timing_manager.bpm_string,
            'stops': self._parent.timing_manager.ms_stops_string,
            'measures': notes,
            'audio_name': audio_out_file
        })

        result = result.encode('utf-8', errors='ignore')
        tqdm.write('Writing SM file')
        try:
            with open(self._parent.SM_file_path, 'wb') as f:
                f.write(result)
        except IOError:
            tqdm.write('Error while opening SM file')
            raise

    def make_file_setter(self, field):
        setter = self.make_setter(field)

        def inner(new_value):
            self._parent.add_file_to_copy(new_value)
            setter(new_value)

        return inner

    def make_setter(self, field):
        """Create a setter for a metadata `field`"""
        return partial(operator.setitem, self._meta_data, field)

    @transform_args(..., CastableToInt)
    def set_difficulty(self, difficulty):
        if difficulty not in (1, 2, 3, 4, 5):
            raise UnknownDifficulty
        diff_names = (None, 'Beginner', 'Medium', 'Hard', 'Insane', 'Edit')
        self._meta_data['difficulty'] = difficulty
        self._meta_data['difficulty_name'] = diff_names[difficulty]
