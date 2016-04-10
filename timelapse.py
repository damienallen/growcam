import os
import sys
import argparse
import logging
from PIL import Image, ImageStat
from moviepy.editor import ImageSequenceClip, TextClip, CompositeVideoClip, concatenate_videoclips
from datetime import datetime, timedelta


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
parser.add_argument('-x','--date', help='Timelapse for specified date (YYYYMMDD)', required=False)
parser.add_argument('-d','--days', help='Timelapse for specified number of days', required=False)
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

# make sure only one date filter is applied
if args.date and (args.start or args.end or args.days):
    logger.error('\'date\' argument cannot be used with start/end dates or number of days')
    sys.exit()

if args.days and (args.start or args.end or args.date):
    logger.error('\'days\' argument cannot be used with start/end/specific dates')
    sys.exit()

# filter images to specified dates
if args.start and not args.end:
    logger.debug('Filtering using start date: %s', args.start)
    valid_dates = [x for x in image_files if int(x[8:16]) >= int(args.start)]

elif args.start and args.end:
    logger.debug('Filtering to date range: %s - %s', args.start, args.end)
    valid_dates = [x for x in image_files if int(x[8:16]) >= int(args.start) and int(x[8:16]) <= int(args.end)]

elif not args.start and args.end:
    logger.debug('Filtering using end date: %s',args.end)
    valid_dates = [x for x in image_files if int(x[8:16]) <= int(args.end)]

elif args.date:
    logger.debug('Filtering to day: %s', args.date)
    valid_dates = [x for x in image_files if int(x[8:16]) == int(args.date)]

elif args.days:

    start_date = datetime.now() - timedelta(int(args.days))
    end_date = datetime.now() - timedelta(1)

    start_string = str(start_date.year) + str(start_date.month).zfill(2) + str(start_date.day).zfill(2)
    end_string = str(end_date.year) + str(end_date.month).zfill(2) + str(end_date.day).zfill(2)

    valid_dates = [x for x in image_files if int(x[8:16]) >= int(start_string) and int(x[8:16]) <= int(end_string)]

else:
    valid_dates = [x for x in image_files]

# filter dark images
bad_images = []

def brightness(im_file):
    global bad_images

    try:
        im = Image.open(input_dir + im_file).convert('L')
        stat = ImageStat.Stat(im)
        return stat.mean[0]

    except OSError:
        logger.warn('Bad image: %s', im_file)
        bad_images += [im_file]
        return 0

if args.threshold:
    thresh = args.threshold
else:
    thresh = 30

logger.debug('Applying brightness threshold of %s', thresh)

if not args.all:
    input_files = [x for x in valid_dates if brightness(x) >= thresh and not x in bad_images]

else:
    input_files = [x for x in valid_dates if not x in bad_images]

# get other command line arguments
if not args.fps:
    fps = 15
    logger.debug('No FPS specified, using 15 fps by default.')
else:
    fps = int(args.fps)

# get paths for input files
if not input_files:
    logger.error('Zero results found within date filter.')
    sys.exit()

# split into clips for each hour
hour = input_files[0][17:19]
input_paths = []
clips = []

for x in input_files:
    if x[17:19] == hour:
        input_paths += [input_dir + x]

    else:
        timestamp = '%s/%s/%s | %s:00' % (x[8:12], x[12:14], x[14:16], x[17:19])

        image_clip = ImageSequenceClip(input_paths, fps=fps)
        timestamp_clip = TextClip(timestamp, color='white', font='arial', fontsize=24, size=image_clip.size).set_duration(image_clip.duration).set_position((-500,350))

        clips += [CompositeVideoClip([image_clip, timestamp_clip])]

        input_paths = [input_dir + x]
        hour = x[17:19]


# print(clips)
# w,h = moviesize = clip.size

# build input file paths
# input_paths = [input_dir + x for x in input_files]

# set output file path
if args.date:
    output_path = output_dir + 'timelapse_' + str(input_files[0][8:16]) + '.mp4'

elif args.days:
    output_path = output_dir + 'timelapse_' + str(args.days) + 'd.mp4'

else:
    output_path = output_dir + 'timelapse_' + str(input_files[0][8:16]) + '-' +  str(input_files[-1][8:16]) + '.mp4'

# write compiled video
final_clip = concatenate_videoclips(clips)
final_clip.write_videofile(output_path, audio=False)

# exit
logger.debug('Finished!')
sys.exit()