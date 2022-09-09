from time import sleep
import requests

def switchDevice(device, on):

    controlPart = ''

    if device["type"] == "relay":
        controlPart = '/device/relay/control'

    url = f'{device["api_url"]}{controlPart}'

    payload = device["parameter"]
    payload[device["on_off_parameter_name"]] = device["on_parameter_value"] if on else device["off_parameter_value"]

    response = requests.request("POST", url, data=payload)

    # Make sure that the shelly api is not called twice in a second. This is a dirty workaround!
    sleep(1.5)

    return response.json()["isok"]