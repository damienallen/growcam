import requests

HOST = 'http://localhost:8000'


def post_observation_data(temperature, pressure, humidity, resistance):

    # Get auth token from server
    auth_request = requests.post(
        HOST + '/api/auth/token/',
        data = {
            'username': 'test_user',
            'password': 'pass1234'
        }
    )

    auth_response = auth_request.json()

    if auth_request.status_code == 200:
        token = auth_response['token']
        auth_header = {'Authorization': 'Token %s' % token}

    else:
        raise Exception('Call to authentication endpoint failed.\n[%s] %s: %s' %\
        (auth_response['status']['code'], auth_response['status']['text'], auth_response['data']['detail']))

    # Send observation to server
    observation_data = {
        'temperature': temperature,
        'pressure': pressure,
        'humidity': humidity,
        'resistance': resistance
    }


    ovservation_url = HOST + '/api/observations/'
    observation_request = requests.post(ovservation_url, data=observation_data, headers=auth_header)
    print(observation_request.json())
