import re
import sys

sys.path.append('..')

from devices.shelly import ShellyApiConnector
from Logger import log
from urllib3 import encode_multipart_formdata
from tkinter import N
import json
from time import time

class DeviceController:

    def readDevicesFromConfigFile(self):
        f = open('../deviceconfig.json')
        return json.load(f)

    def __combine(self, device, state):
        theState = state
        if theState is None:
            theState = {
                "state": 0,
                "timestamp": 0,
                "temperature_c": None,
                "temperature_f": None,
                "humidity": None,
                "consumption": None,
                "lastChange": 0,
                "forced": 0
            }
        device.update(theState)
        return device

    def __calculateNeededPower(self, device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
        if device["priority"] < 34:
            return device["estimated_consumption"] - restWithBattery
        elif device["priority"] > 34 and device["priority"] < 67:
            return device["estimated_consumption"] - restWithBatteryPartially
        else:
            return device["estimated_consumption"] - restWithoutBattery

    def __isOverpowered(self, device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
        if device["priority"] < 34:
            return restWithBattery < 0
        elif device["priority"] > 34 and device["priority"] < 67:
            return restWithBatteryPartially < 0
        else:
            return restWithoutBattery < 0

    def __isDeviceBelowExcess(self, device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
        if device["priority"] < 34:
            return device["estimated_consumption"] <= restWithBattery
        elif device["priority"] > 34 and device["priority"] < 67:
            return device["estimated_consumption"] <= restWithBatteryPartially
        else:
            return device["estimated_consumption"] <= restWithoutBattery
    
    def __isFullfillingCondition(self, device, dbConnection):
        if 'condition' in device:
            condition = device['condition']
            currentDeviceStatus = dbConnection.getCurrentDeviceStatus(condition['device'])

            fieldValue = currentDeviceStatus[condition['field']]

            if fieldValue is None:
                return False
            
            if condition['comparision'] == '>':
                return  fieldValue> condition['value']
            elif condition['comparision'] == '<':
                return fieldValue < condition['value']
            elif condition['comparision'] == '>=':
                return fieldValue >= condition['value']
            elif condition['comparision'] == '<=':
                return fieldValue <= condition['value']
            elif condition['comparision'] == '==':
                return fieldValue == condition['value']
            elif condition['comparision'] == '!=':
                return fieldValue != condition['value']
            else:
                return False

        else:
            return True


    def __switchOffDevices(self, devices, needed, isMandatory):
        switchedOff = 0

        toDo = {}

        index = 0
        while switchedOff < needed and index < len(devices):
            device = devices[index]
            if device['lastChange'] is None or time() - device["lastChange"] > device["min_on_time"]:
                toDo[device["identifier"]] = { 
                    'on': False, 
                    'reason': "not enough power available" if isMandatory else "clear needed power" 
                }
                switchedOff += device["consumption"]
            index += 1

        return toDo if isMandatory or switchedOff >= needed else None

    def switchDevice(self, device, on, reason, dbConnection, forced=False):

        result = False

        if device["device"] == "shelly":
            result = ShellyApiConnector.switchDevice(device, on)

        if result:
            print(f"Did switch device {device['identifier']} {'on' if on else 'off'} because {reason}.")
            log(f"Did switch device {device['identifier']} {'on' if on else 'off'} because {reason}.")
            try:
                dbConnection.saveCurrentDeviceStatus(device['identifier'], state=1 if on else 0, lastChange=time(), forced=forced)
            except Exception as err:
                log(f"failed to save device state: {err}")
            

    
    def readSensorData(self, dbConnection):
        deviceConfig = self.readDevicesFromConfigFile()

        for device in deviceConfig:
            if device['device'] == "shelly":
                data = ShellyApiConnector.readSensorData(device)
                dbConnection.saveCurrentDeviceStatus(device['identifier'], temperature_c=data['temperature_c'], temperature_f=data['temperature_f'], humidity=data['humidity'], consumption=data['consumption'])
    
    def getDevices(self, dbConnection):
        deviceConfig = self.readDevicesFromConfigFile()

        return list(
            map(lambda item: self.__combine(item, dbConnection.getCurrentDeviceStatus(item['identifier'])), deviceConfig)
        )


    def controlDevices(self, dbConnection, identifier = None):
        currentPVState = dbConnection.getCurrentPVStateMovingAverage()

        devices = self.getDevices(dbConnection)

        if identifier is not None:
            devices = list(filter(lambda item: item["identifier"] == identifier, devices))

        devices = list(filter(lambda item: not item["forced"], devices))

        batteryStateFactor = 0
        if currentPVState["batteryState"] <= 98:
            batteryStateFactor = 1
        elif currentPVState["batteryState"] == 99:
            batteryStateFactor = 0.5
        else:
            batteryStateFactor = 0

        availableWithBattery = (currentPVState["gridOutput"] + (currentPVState["batteryCharge"] - (5 * batteryStateFactor))) * 1000
        availableWithBatteryPartially = (currentPVState["gridOutput"] + (currentPVState["batteryCharge"] - (2 * batteryStateFactor))) * 1000
        availableWithoutBattery = (currentPVState["gridOutput"] + currentPVState["batteryCharge"]) * 1000

        toDo = {}

        onDevicesLowFirst = sorted(
            list(
                filter(
                    lambda device: device["state"] == 1 and 'priority' in device, 
                    devices
                )
            ), 
            key=lambda i: i['priority']
        )

        for device in list(onDevicesLowFirst):

            if not self.__isFullfillingCondition(device, dbConnection) or self.__isOverpowered(device, availableWithBattery, availableWithBatteryPartially, availableWithoutBattery):
                if device['lastChange'] is None or time() - device['lastChange'] > device['min_on_time']:
                    toDo[device["identifier"]] = { 
                        'on': False, 
                        'reason': "condition not fullfilled or not enough power available"
                    }
                    onDevicesLowFirst.remove(device)
                    availableWithBattery = availableWithBattery + device['consumption']
                    availableWithBatteryPartially = availableWithBatteryPartially + device['consumption']
                    availableWithoutBattery = availableWithoutBattery + device['consumption']

        offDevicesHighFirst = sorted(
            list(
                filter(
                    lambda device: (device["state"] == 0 or device['state'] is None) and 'priority' in device,
                    devices
                )
            ), 
            key=lambda i: i['priority'],
            reverse=True
        )

        if len(offDevicesHighFirst) > 0:

            highestPrioDeviceHandled = False

            for device in offDevicesHighFirst:
                if self.__isDeviceBelowExcess(device, availableWithBattery, availableWithBatteryPartially, availableWithoutBattery) and self.__isFullfillingCondition(device, dbConnection):
                    if (highestPrioDeviceHandled and device["use_waiting_power"]) or not highestPrioDeviceHandled:
                        if device['lastChange'] is None or time() - device["lastChange"] > device["min_off_time"]:
                            toDo[device["identifier"]] = { 
                                                            'on': True, 
                                                            'reason': "enought power available"
                                                        }
                            availableWithBattery = max(availableWithBattery - device["estimated_consumption"], 0)
                            availableWithBatteryPartially = max(availableWithBatteryPartially - device["estimated_consumption"], 0)
                            availableWithoutBattery = max(availableWithoutBattery - device["estimated_consumption"], 0)

                elif self.__isFullfillingCondition(device, dbConnection):
                    highestPrioDeviceHandled = True
                    
                    if time() - device["timestamp"] > device["min_off_time"]:
                        needed = self.__calculateNeededPower(device, availableWithBattery, availableWithBatteryPartially, availableWithoutBattery)

                        tryToSwitchOff = self.__switchOffDevices(
                            list(filter(
                                lambda lowerDevice: lowerDevice["priority"] <= device["priority"],
                                onDevicesLowFirst
                            )), 
                            needed, 
                            False
                        )

                        if tryToSwitchOff is not None:
                            toDo.update(tryToSwitchOff)
                            toDo[device["identifier"]] = { 
                                                        'on': True, 
                                                        'reason': "cleared enough power"
                                                    }

        for identifier, on in toDo.items():
            self.switchDevice(
                next(filter(lambda item: item["identifier"] == identifier, devices)),
                on['on'],
                on['reason'],
                dbConnection
            )



