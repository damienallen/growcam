import os
import urllib
import logging
from datetime import datetime
from time import sleep
from PIL import Image


# set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create logging file handler
handler = logging.FileHandler('growcam.log')
handler.setLevel(logging.INFO)

# set logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add handler to logger
logger.addHandler(handler)

# set dropbox directory
data_dir = '/media/growdata/Dropbox/Make/Growcam/tmp/'
os.chdir(data_dir)
logger.debug('Temp data directory set to: %s', data_dir)

# set growcam ip
cam_ip = 'http://10.0.4.43:8080'
logger.debug('Camera IP: %s', cam_ip)


# get current time
dt = datetime.now()

# get filename and file path
file_name = 'growcam_%s_%s.jpg' % (str(dt.year) + str(dt.month).zfill(2) + str(dt.day).zfill(2),
                                  str(dt.hour).zfill(2) + str(dt.minute).zfill(2))
file_path = data_dir + file_name

# attempt capture
logger.debug('Attempting image capture.')

fail_count = 0
wait_time = [10, 30, 60, 300]

while fail_count < 4:

    try:
        if dt.hour in [0,3,6,9,12,15,18,21] and dt.minute == 30:
            urllib.urlopen(cam_ip + '/focus')
            sleep(10)
            
        urllib.urlretrieve(cam_ip + '/photo.jpg', file_name)

        image_file = Image.open(file_name)
        image_file = image_file.rotate(180)
        image_file.save(file_name, quality=80)

        break

    except IOError:
        logger.error('Failed %s time(s), waiting %s seconds.', str(fail_count+1), wait_time[fail_count])
        sleep(wait_time[fail_count])
        fail_count += 1

    except Exception, e:
        logger.error('Unexpected error', exc_info=True)

logger.debug('%s -> %s', cam_ip, file_name)

if fail_count == 0:
    logger.debug('Suceeded on first try.')

elif fail_count > 0 and fail_count < 4:
    logger.warn('Succeeded after %s attempts.', fail_count)

else:
    logger.error('Image capture failed, skipping timestep.')
