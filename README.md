## What is this?

This is a one-way converter of BM files to SM files.
BM stands for BeatMania and is a family of formats used by BeatMania itself and its derivatives.
SM stands for StepMania and is a format used by Stepmania itself and its derivatives.

## Installation

This project is written for Python 3.5+ and has three dependencies: tqdm (for progress bars), pydub (for audio stuff) and chardet.
To install, type the following into terminal:

`pip install chardet pydub tqdm`

If you are on Windows, colorama is also recommended for tqdm.

`pip install colorama`

Pydub itself is dependent on either ffmpeg or libav. Refer to [pydub repository](https://github.com/jiaaro/pydub) for installation instructions.

After then, just run the script as a regular Python script

`python3 BM2SMConverter.py -h`

This should print out usage message.

```
usage: BM2SMConverter.py [-h] [-I IN_FILE] [-O OUT_DIR] [-K KEYS]
                         [-M {ALL,SM,AUDIO}] [-V]

Convert BM files to SM

optional arguments:
  -h, --help            show this help message and exit
  -I IN_FILE, --in_file IN_FILE
                        Path to file to be converted.
  -O OUT_DIR, --out_dir OUT_DIR
                        Where to write converted files. Default: Same
                        directory as specified in --in_file
  -K KEYS, --keys KEYS  How keys from BM? chart map onto SM chart. Should be a
                        string no less than 4 and no higher than 8 character.
                        1-7 means KEY1-KEY7, S means scratch track, X means
                        empty track. Only leftmost value is used, so
                        duplicated values are treated the same as X. Default:
                        S1234567
  -M {ALL,SM,AUDIO}, --mode {ALL,SM,AUDIO}
                        Converter mode, useful for batch conversion. SM will
                        only convert to SM chart. AUDIO only bakes OGG audio
                        file. ALL does both. Default: ALL.
  -V, --verbose         Verbose mode, will print all kinds of messages if set.
```

## Notes

[This site](https://hitkey.nekokan.dyndns.info/cmds.htm) was used as a reference for parsing BM files.

## Common errors

* ValueError: Usually indicates an error with one of the values in the chart, such as negative BPM or incorrect stop. May also indicate an internal error.

* NotPlayer1Error: The chart is not for player 1. Such charts are planned to be supported in the future.

* UnsupportedControlFlowError: The chart uses control flow gimmicks. There is no way to represent this in Stepmania. Support is not planned, but possible.

* StopIsNotDefined: Somewhere in the chart there is a stop invokation that has not been defined in any #STOP.

* BPMIsNotDefined: Same as StopIsNotDefined, but for #BPM.

* FirstHoldHasNoStart: Will only occur if the chart uses LNOBJ for LNs and the very first LN does not have a note preceding it on this lane.

* LNTypeUnsupportedError: Should never happen unless a new appropriate value of LNTYPE is defined for BM format.

* UndecidableAudioFile: This audio file is either not present at all or there are multiple candidates. Planned to be ignorable in future for unsafe mode.

* UnknownDifficulty: Invalid value was supplied for #DIFFICULTY.

* EmptyChart: This chart has no objects.

* BeatStopTooShort: May happen on gimmick charts. Due to SM only supporting 1 ms stops at best, if one of the stops in BM chart is less than that, then there is no way to represent this in SM chart. Planned to be ignorable in unsafe mode in future.

* UnsupportedGameMode: Raised if there is no game mode for this amount of keys.

## License

This project is licensed under the GPLv3 license, refer to [LICENSE](https://github.com/DeltaEpsilon7787/BM2SMConverter/blob/master/LICENSE) for details.
