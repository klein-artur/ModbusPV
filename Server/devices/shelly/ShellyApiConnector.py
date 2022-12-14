from time import sleep
from Logger import log
import requests

def readSensorData(device):
    url = f'{device["api_url"]}/device/status'

    response = requests.request("POST", url, data=device["parameter"])

    # Make sure that the shelly api is not called twice in a second. This is a dirty workaround!
    sleep(1.5)

    data = response.json()

    if data['isok']:
        if device['type'] == 'sensor':
            return {
                'temperature_c': data['data']['device_status']['temperature:0']['tC'],
                'temperature_f': data['data']['device_status']['temperature:0']['tF'],
                'humidity': data['data']['device_status']['humidity:0']['rh'],
                'consumption': None
            }
        else:
            deviceStatus = data['data']['device_status']

            consumption = 0.0
            if "meters" in deviceStatus:
                consumption = deviceStatus['meters'][0]['power']
            else:
                consumption = deviceStatus['switch:0']['apower']

            return {
                'temperature_c': None,
                'temperature_f': None,
                'humidity': None,
                'consumption': consumption
            }
    

def switchDevice(device, on):

    controlPart = ''

    if device["type"] == "relay":
        controlPart = '/device/relay/control'

    url = f'{device["api_url"]}{controlPart}'

    payload = device["parameter"]
    payload['turn'] = 'on' if on else 'off'

    response = requests.request("POST", url, data=payload)

    # Make sure that the shelly api is not called twice in a second. This is a dirty workaround!
    sleep(1.5)

    responseJson = response.json()

    print(responseJson)
    log(responseJson)

    return response.json()["isok"]