#!/home/pi/growcam/venv/bin/python
try:
    from picamera import PiCamera
    camera_available = True
    print('\nCamera: Active')
except ImportError:
    camera_available = False
    print('\nCamera: Inactive')

print('Initiating bme680 sensor')
import smbus
import bme680
import time
import requests
import numpy as np


# Get auth details
from secret import GROWLOGGER_HOST, GROWLOGGER_USERNAME, GROWLOGGER_PASSWORD

# Initiate a PiCamera instance
if camera_available:
    camera = PiCamera()
    camera.start_preview()
    photo_path = '/home/pi/Desktop/capture.jpg'

# Growlogger host
HOST = GROWLOGGER_HOST

sensor = bme680.BME680()

# These oversampling settings can be tweaked to 
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print("\n\nInitial reading:")
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print("{}: {}".format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Calculate average over 10 seconds
print("\n\nPolling:")
observations = []
for n in range(0, 10):
    if sensor.get_sensor_data():
        raw_temperature = sensor.data.temperature
        calibration_offset = -6
        calibrated_temperature = raw_temperature + calibration_offset

        # Store data values
        observations += [[calibrated_temperature, sensor.data.pressure,sensor.data.humidity, sensor.data.gas_resistance]]

        # Print output
        output = "{0:.2f} C, {1:.2f} hPa, {2:.2f} %RH".format(calibrated_temperature, sensor.data.pressure, sensor.data.humidity)
        if sensor.data.heat_stable:
            print(" {0},{1} Ohms".format(output, sensor.data.gas_resistance))
        else:
            print(output)

    time.sleep(1)
	
# Capture image
if camera_available:
    camera.rotation = 180
    camera.capture(photo_path)
    camera.stop_preview()

# Numpy operations
np_observations = np.array(observations)
mean_values = np_observations.mean(axis=0)

# Get auth token from server
auth_request = requests.post(
    HOST + '/api/auth/token/',
    data={
        'username': GROWLOGGER_USERNAME,
        'password': GROWLOGGER_PASSWORD
    }
)

auth_response = auth_request.json()

if auth_request.status_code == 200:
    token = auth_response['token']
    auth_header = {'Authorization': 'Token %s' % token}

else:
    raise Exception('Call to authentication endpoint failed.\n[%s] %s: %s' % \
                    (auth_response['status']['code'], auth_response['status']['text'],
                     auth_response['data']['detail']))

# Send observation to server
observation_data = {
    'temperature': round(mean_values[0], 2),
    'pressure': round(mean_values[1], 2),
    'humidity': round(mean_values[2], 2),
    'resistance': int(mean_values[3]),
    'camera_name': "Hobby Room",
    'nir_filter': True
}

photo_file = {'file': open(photo_path, 'rb')} if camera_available else None
observation_url = HOST + '/api/observations/'
observation_request = requests.post(observation_url, files=photo_file, data=observation_data, headers=auth_header)

print('\nResponse:')
print(observation_request.json())
