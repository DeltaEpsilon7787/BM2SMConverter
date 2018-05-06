## What is this?

This is a one-way converter of BM files to SM files.
BM stands for BeatMania and is a family of formats used by BeatMania itself and its derivatives.
SM stands for StepMania and is a format used by Stepmania itself and its derivatives.

## Installation

This project is written for Python 3.5+ and has three dependencies: tqdm (for progress bars), pydub (for audio stuff) and chardet.
To install, type the following into terminal:

`pip install chardet pydub tqdm`

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

## License

This project is licensed under the GPLv3 license, refer to [LICENSE](https://github.com/DeltaEpsilon7787/BM2SMConverter/blob/master/LICENSE) for details.