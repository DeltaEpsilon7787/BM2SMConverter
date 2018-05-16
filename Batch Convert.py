## Instructions (Python 3.5+ and running on Japanese/Korean Locale)
# 1. Edit the 'inputs' and 'output' directory which contains the library of BMS files
#    you want to convert and where to output.
# 2. Run this script.
# 3. In the same directory you placed the Python script, search for convert.bat (or whatever
#    you set for 'output_list', and place it in the folder with SM2BMConverter.exe, then run the .bat file.

## Example:
# BM2SMConverter.exe -I "D:/Insane BMS/2016-08-21 proposals/love_this_moment_ogg/love_this_moment_n.bme" -O "D:/BMS SM Convert/love_this_moment_ogg love_this_moment_n" -K S1234567

## NOTES:
# This script assists in converting a very large collection of BMS files.
# For example, if you have the Insane BMS folder, you can convert just
# about every possible file. This script does not search through subdirectories
# however.
#
# Folders are named after their parent folder (song) and filename without the extension.

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
            for f in glob.iglob("D:/Insane BMS/2016-08-21 proposals/" + e + "/*." + formats): # iterate through a list of BMS files 
                f = f.replace("\\", "/")
                unique_file = re.search("^.*/([^.]*)..*$", f, re.X) # grab file name from BMS file path
                # generate command and add into 'output_list'
                command = ('BM2SMConverter.exe -I \"' + f + '\"' + ' -O ' + '\"' + output + e + " " + unique_file.group(1) + '\" -K ' + keys + ' -M ' + convert_type + ' -V')
                with open(output_list, 'a+', encoding="utf-8") as batch:
                    batch.write(command + '\n') # write each individual conversion command into a file

create_convert_list() # runs the command above
                

## Issues:
# Cannot convert folders with parantheses. 
