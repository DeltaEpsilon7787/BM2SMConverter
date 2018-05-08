import operator
from audioop import add as audio_add
from typing import List

from pydub import AudioSegment
from tqdm import tqdm

from bm2sm.data_structures import Sound
from bm2sm.definitions import DEFAULT_FRAME_RATE, standard_tqdm
from bm2sm.exceptions import EmptyChart
from modules.decorators import transform_return
from modules.fake_types import CastableToInt


class OGGConverter(object):
    """A class where audio baking is done."""

    parent = ...  # type: 'BMChartParser'
    sounds = ...  # type: List[Sound]

    def __init__(self, parent):
        self.parent = parent
        self.sounds = []

    # The basic idea of this algorithm is as follows
    #   0. Sync all sounds, create a silent track of certain length.
    #   1. Sort all sounds, by duration and by starting time.
    #   2. Starting from a null track, add sounds in such a way
    #        so that different sounds never intersect and overlap as such
    #   3. Mix this track with previously created silent track
    #   4. Repeat until all sounds have been exhausted
    #   5. Previously created silent track is now the audio, output into a file
    #
    # This does NOT allow sounds to be interrupted by another sound
    #   so tracks utilizing this effect won't sound the same.
    def bake_audio(self):
        if len(self.sounds) == 0:
            raise EmptyChart
        self.sync_everything()

        song_length_in_frames = self.get_song_length_in_frames()

        # Do you like immutability, punk?
        #   No you don't. Fuck you.
        common_sound = self.sounds[0].sound
        sample_width = common_sound.sample_width
        channels = common_sound.channels

        multiplier = sample_width * channels
        silence_datum = b'\0' * multiplier

        sounds_to_process = self.sounds
        result = silence_datum * song_length_in_frames

        overall_progress = standard_tqdm(desc='Processing track #1', total=len(sounds_to_process))
        track_counter = 1
        while len(sounds_to_process):
            sounds_processed_this_time = 0

            sounds_to_process.sort(key=operator.attrgetter('duration_frames'))
            sounds_to_process.sort(key=operator.attrgetter('start_time_frames'))

            data_fragments = []
            unprocessed_sounds = []

            last_frame = 0

            with standard_tqdm(iterable=sounds_to_process, leave=False) as progress_sounds_to_process:
                for sound in progress_sounds_to_process:
                    start_frame = sound.start_time_frames
                    end_frame = sound.end_time_frames
                    if start_frame >= last_frame:
                        padding_silence = silence_datum * (start_frame - last_frame)
                        data_fragments.append(padding_silence)
                        data_fragments.append(sound.sound.raw_data)
                        last_frame = end_frame
                        sounds_processed_this_time += 1
                    else:
                        unprocessed_sounds.append(sound)

            imposed_data = b''.join(data_fragments)
            finishing_silence = silence_datum * (song_length_in_frames -
                                                 last_frame)
            data_fragments.clear()
            imposed_data = b''.join((imposed_data, finishing_silence))
            result = audio_add(result, imposed_data, sample_width)
            sounds_to_process = unprocessed_sounds
            track_counter += 1
            overall_progress.set_description('Processing track #{}'.format(track_counter))
            overall_progress.update(sounds_processed_this_time)

        overall_progress.close()
        tqdm.write('Writing OGG file')
        output = AudioSegment(data=result,
                              channels=channels,
                              frame_rate=DEFAULT_FRAME_RATE,
                              sample_width=sample_width)

        output.export(self.parent.OGG_file_path,
                      format='ogg')

    @transform_return(CastableToInt)
    def get_song_length_in_frames(self):
        last_sound = max(self.sounds,
                         key=operator.attrgetter('end_time_frames'))
        return last_sound.end_time_frames

    # noinspection PyProtectedMember
    def sync_everything(self):
        data = [(T, T.sound) for T in self.sounds]
        sound, segments = zip(*data)

        # Regular syncing creates copies of the sound
        #   And this is slow as hell
        # So a small hack is used as a workaround
        synced_segments = AudioSegment._sync(*segments)
        result = zip(sound, synced_segments)
        for sound, synced_segment in result:
            sound.sound = synced_segment
