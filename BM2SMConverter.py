# coding: utf-8

# Following site is used for reference
# https://hitkey.nekokan.dyndns.info/cmds.htm

# Abandon all hope ye who enter here


import sys
from argparse import ArgumentParser
from io import StringIO
from os import makedirs, path

from tqdm import tqdm

import bm2sm.BM_parser

tqdm.monitor_interval = 0

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Convert BM files to SM',
                                add_help=True,
                                allow_abbrev=True)

    arg_parser.add_argument('-I', '--in_file',
                            action='store',
                            help='Path to file to be converted.',
                            required=True,
                            type=str)

    arg_parser.add_argument('-O', '--out_dir',
                            action='store',
                            default=None,
                            help='Where to write converted files. Default: Same directory as specified in --in_file.',
                            type=str)

    arg_parser.add_argument('-K', '--keys',
                            action='store',
                            default='S1234567',
                            help="How the keys from BM chart map onto SM chart. Accepted string lengths: 4, 5, 6, 7, "
                                 "8, 10 characters. 1-7 means KEY1-KEY7, S means scratch track, X means empty "
                                 "track. Only leftmost value is used, so duplicated values are treated the same as X. "
                                 "Default: S1234567",
                            type=str)

    arg_parser.add_argument('-M', '--mode',
                            action='store',
                            choices=['ALL', 'SM', 'AUDIO'],
                            default='ALL',
                            help='Converter mode, useful for batch conversion. '
                                 'SM will only convert to SM chart. AUDIO only bakes OGG audio file. '
                                 'ALL does both. '
                                 'Default: ALL.')

    arg_parser.add_argument('-V', '--verbose',
                            action='store_true',
                            default=False,
                            help='Verbose mode, will print all kinds of messages if set.')

    args = arg_parser.parse_args()

    if args.out_dir and not path.exists(args.out_dir):
        makedirs(args.out_dir)

    if not args.verbose:
        sys.stdout = StringIO()  # Null file
        sys.stderr = StringIO()  # Another one for progress bars

    if not args.out_dir:
        args.out_dir = path.split(args.in_file)[0]

    parser = bm2sm.BM_parser.BMChartParser(args.in_file, args.out_dir, args.keys, args.mode != 'SM')

    if args.mode != 'AUDIO':
        parser.SM_converter.compose_chart()

    if args.mode != 'SM':
        parser.OGG_converter.bake_audio()

    parser.copy_files()
