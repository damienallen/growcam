import os
import sys
import argparse
import logging
from PIL import Image, ImageStat
from moviepy.editor import *


# set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create logging file handler
handler = logging.FileHandler('growcam_timelapse.log')
handler.setLevel(logging.INFO)

# set logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add handler to logger
logger.addHandler(handler)

# set up command line argument parser
parser = argparse.ArgumentParser(description='This script creates timelapse videos using supplied frames (jpg or png).')
parser.add_argument('-i','--input', help='Input directory (images)', required=False)
parser.add_argument('-o','--output', help='Output directory (resulting videos)', required=False)
parser.add_argument('-s','--start', help='Start date (YYYYMMDD)', required=False)
parser.add_argument('-e','--end', help='End date (YYYYMMDD)', required=False)
parser.add_argument('-d','--day', help='Timelapse for specified day (YYYYMMDD)', required=False)
parser.add_argument('-f','--fps', help='Framerate (frames/s)', required=False)
parser.add_argument('-t','--threshold', help='Brightness filter threshold (0-255)', required=False)
parser.add_argument('-a','--all', help='Use all frames (including dark images)', action='store_true', required=False)
args = parser.parse_args()

# set file directories
if not args.input:
    input_dir = 'Y:\\Growcam\\'
    logger.debug('No input directory specified, falling back to hardcoded default.')
else:
    input_dir = args.input

if not args.output:
    output_dir = 'Y:\\Growcam\\timelapse\\'
    logger.debug('No output directory specified, falling back to hardcoded default.')
else:
    output_dir = args.output

logger.debug('Archive directory set to: %s', input_dir)
logger.debug('Timelapse directory set to: %s', output_dir)

# get file list
all_files = os.listdir(input_dir)
image_files = [x for x in all_files if os.path.splitext(x)[1] in ['.jpg','.jpeg','.png']]

if not image_files:
    logger.error('Input directory contains no jpg or png files.')
    sys.exit()

if args.day and (args.start or args.end):
    logger.error('\'day\' argument cannot be used with start/end dates')
    sys.exit()

# filter images to specified dates
if args.start and not args.end:
    logger.debug('Filtering using start date: %s', args.start)
    valid_dates = [x for x in image_files if int(x[8:16]) > int(args.start)]

elif args.start and args.end:
    logger.debug('Filtering to date range: %s - %s', args.start, args.end)
    valid_dates = [x for x in image_files if int(x[8:16]) > int(args.start) and int(x[8:16]) < int(args.end)]

elif not args.start and args.end:
    logger.debug('Filtering using end date: %s',args.end)
    valid_dates = [x for x in image_files if int(x[8:16]) < int(args.end)]

elif args.day:
    logger.debug('Filtering to day: %s', args.day)
    valid_dates = [x for x in image_files if int(x[8:16]) == int(args.day)]

else:
    valid_dates = [x for x in image_files]

# filter dark images
if not args.all:

    def brightness(im_file):
        im = Image.open(input_dir + im_file).convert('L')
        stat = ImageStat.Stat(im)
        return stat.mean[0]

    if args.threshold:
        thresh = args.threshold
    else:
        thresh = 20

    logger.debug('Applying brightness threshold of %s', thresh)

    input_files = [x for x in valid_dates if brightness(x) >= thresh]

else:
    input_files = valid_dates

    
# get other command line arguments
if not args.fps:
    fps = 15
    logger.debug('No FPS specified, using 15 fps by default.')
else:
    fps = args.fps

# get paths for input files
if not input_files:
    logger.error('Zero results found within date filter.')
    sys.exit()

input_paths = [input_dir + x for x in input_files]

# create video using moviepy
clip = ImageSequenceClip(input_paths, fps=fps)

if args.day:
    output_path = output_dir + 'timelapse_' + str(input_files[0][8:16]) + '.webm'

else:
    output_path = output_dir + 'timelapse_' + str(input_files[0][8:16]) + '-' +  str(input_files[-1][8:16]) + '.webm'

clip.write_videofile(output_path, audio=False)
