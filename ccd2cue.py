#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
https://github.com/crumpx/ccd2cue.git
'''

import configparser
import os
from datetime import timedelta

def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def CCD2CUE(ccdsheet):
    filename = os.path.splitext(ccdsheet)
    cuesheet = os.path.join(filename[0]+'.cue')
    imagetype=('.img','.bin','.iso')
    imgfile = ''
    basedir = os.path.dirname(ccdsheet)
    files = list(filter(lambda f: os.path.isfile(os.path.join(basedir,f)), os.listdir(basedir)))
    for f in files:

        if os.path.splitext(f)[1].casefold() in map(str.casefold, imagetype):
            imgfile = f

    Config = configparser.ConfigParser()
    Config.read(ccdsheet)
    cuefile = open(cuesheet, 'w')

    track_counter = 0
    BEGIN = False

    cuefile.write("FILE \"%s\" BINARY\n" % (imgfile))
    for item in Config.sections():
        if 'Entry' not in item:
            continue

        trackinfo = {}
        tracktype = ConfigSectionMap(Config,item)['control']
        trackindex = int(ConfigSectionMap(Config,item)['session'])
        trackinfo['minute'] = int(ConfigSectionMap(Config, item)['pmin'])
        trackinfo['second'] = int(ConfigSectionMap(Config,item)['psec'])
        trackinfo['frame'] = int(ConfigSectionMap(Config,item)['pframe'])
        


        if int(ConfigSectionMap(Config,item)['plba']) == 0:
            BEGIN = True

        if BEGIN:
        
            track_counter += 1
            
            if track_counter == 1:
                cuefile.write("  TRACK 01 MODE1/2352\n" \
                              "    INDEX 01 00:00:00\n")
            else:
                index0 = timedelta(minutes=trackinfo['minute'],seconds=trackinfo['second']) - timedelta(seconds=4)                  
                index0_m = int(index0.seconds/60)
                index0_s = int(index0.seconds - index0_m*60)
                
                index1 = timedelta(minutes=trackinfo['minute'],seconds=trackinfo['second']) - timedelta(seconds=2)                  
                index1_m = int(index1.seconds/60)
                index1_s = int(index1.seconds - index1_m*60)
                
                cuefile.write(
                f"""  TRACK {track_counter} AUDIO\n"""
                f"""    INDEX 00 {index0_m:02}:{index0_s:02}:{trackinfo['frame']:0>2}\n"""
                f"""    INDEX 01 {index1_m:02}:{index1_s:02}:{trackinfo['frame']:0>2}\n"""
                )

    cuefile.close()
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--ccd', dest='ccdsheet', required=True, help='ccd file name')
    args = parser.parse_args()
    CCD2CUE(args.ccdsheet)