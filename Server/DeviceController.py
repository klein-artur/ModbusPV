import re
from shelly import ShellyApiConnector
from Logger import log
from urllib3 import encode_multipart_formdata
from tkinter import N
from db.sqliteConnect import getCurrentDeviceStates, saveCurrentDeviceStatus, getCurrentPVStateMovingAverage, getCurrentDeviceStatus
import json
from time import time

class DeviceController:

    def __readDevicesFromConfigFile(self):
        f = open('../deviceconfig.json')
        return json.load(f)

    def __getStateFromList(self, list, identifier):
        result = next(filter(lambda item: item["identifier"] == identifier, list), {
            "identifier": identifier,
            "state": 0,
            "timestamp": 0
        })

        return result

    def __combine(self, device, state):
        device.update(state)
        return device

    def __calculateNeededPower(self, device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
        if device["priority"] < 34:
            return device["needed_power"] - restWithBattery
        elif device["priority"] > 34 and device["priority"] < 67:
            return device["needed_power"] - restWithBatteryPartially
        else:
            return device["needed_power"] - restWithoutBattery

    def __isDeviceBelowExcess(self, device, restWithBattery, restWithBatteryPartially, restWithoutBattery):
        isBelow = False
        if device["priority"] < 34:
            isBelow = device["needed_power"] <= restWithBattery
        elif device["priority"] > 34 and device["priority"] < 67:
            isBelow = device["needed_power"] <= restWithBatteryPartially
        else:
            isBelow = device["needed_power"] <= restWithoutBattery

        return isBelow

    
    def __isFullfillingCondition(self, device):
        if 'condition' in device:
            condition = device['condition']
            currentDeviceStatus = getCurrentDeviceStatus(condition['device'])
            
            if condition['comparision'] == '>':
                return currentDeviceStatus[condition['field']] > condition['value']
            elif condition['comparision'] == '<':
                return currentDeviceStatus[condition['field']] < condition['value']
            elif condition['comparision'] == '>=':
                return currentDeviceStatus[condition['field']] >= condition['value']
            elif condition['comparision'] == '<=':
                return currentDeviceStatus[condition['field']] <= condition['value']
            elif condition['comparision'] == '==':
                return currentDeviceStatus[condition['field']] == condition['value']
            elif condition['comparision'] == '!=':
                return currentDeviceStatus[condition['field']] != condition['value']
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
            if time() - device["timestamp"] > device["min_on_time"]:
                toDo[device["identifier"]] = False
                switchedOff += device["needed_power"]
            index += 1

        return toDo if isMandatory or switchedOff >= needed else None

    def __switchDevice(self, device, on):

        result = False

        if device["device"] == "shelly":
            result = ShellyApiConnector.switchDevice(device, on)

        if result:
            print(f"Did switch device {device['identifier']} {'on' if on else 'off'}")
            log(f"Did switch device {device['identifier']} {'on' if on else 'off'}")
            try:
                saveCurrentDeviceStatus(device['identifier'], 1 if on else 0)
            except Exception as err:
                try:
                    saveCurrentDeviceStatus(device['identifier'], 1 if on else 0)
                except Exception as err:
                    saveCurrentDeviceStatus(device['identifier'], 1 if on else 0)
            

    
    def readSensorData(self):
        deviceConfig = self.__readDevicesFromConfigFile()

        sensorDevices = list(
            filter(
                lambda device: device["type"] == "sensor",
                deviceConfig
            )
        )

        for sensor in sensorDevices:
            if sensor['device'] == "shelly":
                data = ShellyApiConnector.readSensorData(sensor)
                saveCurrentDeviceStatus(sensor['identifier'], temperature_c=data['temperature_c'], temperature_f=data['temperature_f'], humidity=data['humidity'])


    def controlDevices(self):
        currentPVState = getCurrentPVStateMovingAverage()

        deviceStates = getCurrentDeviceStates()
        deviceConfig = self.__readDevicesFromConfigFile()

        devices = list(map(lambda item: self.__combine(item, self.__getStateFromList(deviceStates, item["identifier"])), deviceConfig))

        restWithBattery = currentPVState["gridOutput"] * 1000
        restWithBatteryPartially = (max(currentPVState["batteryCharge"] - 2, 0) + currentPVState["gridOutput"]) * 1000
        restWithoutBattery = (currentPVState["gridOutput"] + currentPVState["batteryCharge"]) * 1000

        hasExcess = restWithoutBattery > 0

        toDo = {}

        onDevicesLowFirst = sorted(
            list(
                filter(
                    lambda device: device["state"] == 1, 
                    devices
                )
            ), 
            key=lambda i: i['priority']
        )

        for device in list(onDevicesLowFirst):
            if not self.__isFullfillingCondition(device):
                toDo[device["identifier"]] = False
                onDevicesLowFirst.remove(device)

        if hasExcess:

            offDevicesHighFirst = sorted(
                list(
                    filter(
                        lambda device: device["state"] == 0, 
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
                    if self.__isDeviceBelowExcess(device, availableWithBattery, availableWithBatteryPartially, availableWithoutBattery) and self.__isFullfillingCondition(device):
                        if (highestPrioDeviceHandled and device["use_waiting_power"]) or not highestPrioDeviceHandled:
                            if time() - device["timestamp"] > device["min_off_time"]:
                                toDo[device["identifier"]] = True
                                availableWithBattery = max(availableWithBattery - device["needed_power"], 0)
                                availableWithBatteryPartially = max(availableWithBatteryPartially - device["needed_power"], 0)
                                availableWithoutBattery = max(availableWithoutBattery - device["needed_power"], 0)

                    elif self.__isFullfillingCondition(device):
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
                                toDo[device["identifier"]] = True

        else:
            needed = abs(restWithoutBattery)

            toDo = self.__switchOffDevices(onDevicesLowFirst, needed, True)

        for identifier, on in toDo.items():
            self.__switchDevice(
                next(filter(lambda item: item["identifier"] == identifier, devices)),
                on
            )



