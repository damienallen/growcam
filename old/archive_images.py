import os
import logging
from shutil import move


# set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create logging file handler
handler = logging.FileHandler('growcam_archive.log')
handler.setLevel(logging.INFO)

# set logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add handler to logger
logger.addHandler(handler)

# set windows dropbox directory and get file list
tmp_dir = 'U:\\Dropbox\\Make\\Growcam\\tmp\\'
archive_dir = 'Y:\\Growcam\\'

logger.debug('Temp directory: %s', tmp_dir)
logger.debug('Archive directory: %s', archive_dir)

image_files = os.listdir(tmp_dir)
logger.debug('%s image(s) found in temp directory.', len(image_files))

if not image_files:
    logger.info('No new images found.')

# move files if they exist
else:
    logger.info('Moving %s image(s) to archive.', len(image_files))

    for i in image_files:

        try:
            move(tmp_dir + i, archive_dir + i)
            logger.debug('Moved %s sucessfully.', i)

        except:
            logger.error('Unexpected error', exc_info=True)

    logger.debug('Archiving completed.')
