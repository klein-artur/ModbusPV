import re
import requests
from urllib3 import encode_multipart_formdata
from tkinter import N
from db.sqliteConnect import getCurrentDeviceStates, saveCurrentDeviceStatus
import json
from time import time, sleep

def readDevicesFromConfigFile():
    f = open('deviceconfig.json')
    return json.load(f)

def getStateFromList(list, identifier):
    result = next(filter(lambda item: item["identifier"] == identifier, list), {
        "identifier": identifier,
        "state": 0,
        "timestamp": 0
    })

    return result

def combine(device, state):
    device.update(state)
    return device


# def selectDevices(devices, restWithBattery, restWithBatteryPartially, restWithoutBattery, isRest, resultDict):
#     isPositive = restWithoutBattery > 0
    
#     if isPositive:
#         offDevices = list(filter(lambda device: device["state"] == 0, devices))
        
#         for device in offDevices:
#             toCheckPower = 0
#             if device["priority"] < 34:
#                 toCheckPower = restWithBattery
#             elif device["priority"] > 34 and device["priority"] < 67:
#                 toCheckPower = restWithBatteryPartially
#             else:
#                 toCheckPower = restWithoutBattery
            
#             if device["needed_power"] <= toCheckPower and time() - device["timestamp"] > device["min_off_time"]:
#                 resultDict[device["identifier"]] = True
#                 break

#     else:

def calculateNeededPower(device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
    if device["priority"] < 34:
        return device["needed_power"] - restWithBattery
    elif device["priority"] > 34 and device["priority"] < 67:
        return device["needed_power"] - restWithBatteryPartially
    else:
        return device["needed_power"] - restWithoutBattery

def isDeviceBelowExcess(device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
    if device["priority"] < 34:
        return device["needed_power"] <= restWithBattery
    elif device["priority"] > 34 and device["priority"] < 67:
        return device["needed_power"] <= restWithBatteryPartially
    else:
        return device["needed_power"] <= restWithoutBattery


def switchOffDevices(devices, needed, isMandatory):
    switchedOff = 0

    toDo = {}

    index = 0
    while switchedOff < needed and index < len(devices):
        toDo[devices[index]["identifier"]] = False
        switchedOff += devices[index]["needed_power"]
        index += 1

    return toDo if isMandatory or switchedOff >= needed else None


def switchDevice(device, on):

    url = device["control_url"]

    payload = device["parameter"]
    payload[device["on_off_parameter_name"]] = device["on_parameter_value"] if on else device["off_parameter_value"]

    response = requests.request("POST", url, data=payload)

    print(f"Did switch device {device['identifier']} {'on' if on else 'off'}")

    if response.json()["isok"]:
        try:
            saveCurrentDeviceStatus(device['identifier'], 1 if on else 0)
        except Exception as err:
            try:
                saveCurrentDeviceStatus(device['identifier'], 1 if on else 0)
            except Exception as err:
                saveCurrentDeviceStatus(device['identifier'], 1 if on else 0)
        


def controlDevices(currentPVState):
    deviceStates = getCurrentDeviceStates()
    deviceConfig = readDevicesFromConfigFile()

    devices = list(map(lambda item: combine(item, getStateFromList(deviceStates, item["identifier"])), deviceConfig))

    restWithBattery = currentPVState["gridOutput"] * 1000
    restWithBatteryPartially = (max(currentPVState["batteryCharge"] - 2, 0) + currentPVState["gridOutput"]) * 1000
    restWithoutBattery = (currentPVState["gridOutput"] + currentPVState["batteryCharge"]) * 1000

    hasExcess = restWithoutBattery > 0

    toDo = {}

    onDevicesLowFirst = sorted(
        list(
            filter(
                lambda device: device["state"] == 1 and time() - device["timestamp"] > device["min_on_time"], 
                devices
            )
        ), 
        key=lambda i: i['priority']
    )

    if hasExcess:

        offDevicesHighFirst = sorted(
            list(
                filter(
                    lambda device: device["state"] == 0 and time() - device["timestamp"] > device["min_off_time"], 
                    devices
                )
            ), 
            key=lambda i: i['priority'],
            reverse=True
        )

        if len(offDevicesHighFirst) > 0:

            availableWithBattery = restWithBattery
            availableWithBatteryPartially = restWithBatteryPartially
            availableWithoutBattery = restWithoutBattery

            highestPrioDeviceHandled = False

            for device in offDevicesHighFirst:
                if isDeviceBelowExcess(device, availableWithBattery, availableWithBatteryPartially, availableWithoutBattery):
                    if (highestPrioDeviceHandled and device["use_waiting_power"]) or not highestPrioDeviceHandled:
                        toDo[device["identifier"]] = True
                        availableWithBattery = max(availableWithBattery - device["needed_power"], 0)
                        availableWithBatteryPartially = max(availableWithBatteryPartially - device["needed_power"], 0)
                        availableWithoutBattery = max(availableWithoutBattery - device["needed_power"], 0)

                else:
                    highestPrioDeviceHandled = True

                    needed = calculateNeededPower(device, availableWithBattery, availableWithBatteryPartially, availableWithoutBattery)

                    tryToSwitchOff = switchOffDevices(
                        list(filter(
                            lambda lowerDevice: lowerDevice["priority"] <= device["priority"],
                            onDevicesLowFirst
                        )), 
                        needed, 
                        False
                    )

                    if tryToSwitchOff is not None:
                        toDo.update(tryToSwitchOff)
                        toDo[device["identifier"]] = True

    else:
        needed = abs(restWithoutBattery)

        toDo = switchOffDevices(onDevicesLowFirst, needed, True)

    for identifier, on in toDo.items():
        switchDevice(
            next(filter(lambda item: item["identifier"] == identifier, devices)),
            on
        )
        sleep(1.5)
