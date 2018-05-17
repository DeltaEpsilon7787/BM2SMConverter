## Instructions (Python 3.5+ and running on Japanese/Korean Locale)
# 1. Edit the 'inputs' and 'output' directory which contains the library of BMS files
#    you want to convert and where to output.
# 2. Run this script.
# 3. Check the output folder.


## NOTES:
# This script assists in converting a very large collection of BMS files.
# For example, if you have the Insane BMS folder, you can convert just
# about every possible file. This script does not search through subdirectories
# however.
#
# Folders are named after their parent folder (song) and filename.
#
# A large BMS collection with odd key layouts like 14+2K (or other non-1P) files will
# generate empty folders. This will not affect successful conversions.
#
# Finally, DO NOT CONVERT OFFICIAL KONAMI MUSIC FILES WITH THIS TOOL!

import os, subprocess
from os import listdir
from os.path import isfile, isdir, join
import glob
import re

inputs = "D:/Insane BMS/2016-08-21 proposals/" # Add a / slash at the end!
output = "D:/BMS SM Convert/" # Add a / slash at the end!
output_list = "convert.bat"
file_formats = ["bms", "bme", "bml"]
convert_type = "ALL" # Options: ALL, SM, AUDIO
keys = "S1234567"

def create_convert_list():
    for e in [x for x in listdir(inputs) if isdir(join(inputs, x))]: # iterate through each directory of your BMS collection
        for formats in file_formats:
            for f in glob.iglob(inputs + e + "/*." + formats): # iterate through a list of BMS files in each directory
                f = f.replace("\\", "/")
                unique_file = os.path.basename(f) # grab file name from BMS file path
                # generate command and add into 'output_list'
                command = 'BM2SMConverter.exe -I \"' + f + '\"' + ' -O ' + '\"' + output + e + " " + unique_file + '\" -K ' + keys + ' -M ' + convert_type + ' -V'
                print (command)
                subprocess.run(command, shell=True)

create_convert_list() # runs the command above
                

## Issues:
# Cannot convert folders with parantheses.
