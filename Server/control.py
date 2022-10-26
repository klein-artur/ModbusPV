#!/usr/bin/env python3
import os

import sys

from devices.DeviceController import DeviceController
from db.mysqlConnect import MySqlConnector

deviceIdentifier = sys.argv[1]
command = sys.argv[2]

splittedCommand = command.split('=')

deviceController = DeviceController()
db = MySqlConnector()

device = db.getCurrentDeviceStatus(deviceIdentifier);
deviceConfig = list(
    filter(
        lambda config: config['identifier'] == deviceIdentifier,
        deviceController.readDevicesFromConfigFile()
    )
)[0]
device.update(deviceConfig)

if splittedCommand[0] == 'switch':

    newState = splittedCommand[1] == 'on'
    newForced = True

    if newState != device['state']:
        deviceController.switchDevice(
            device, 
            newState,
            'by controller',
            db,
            forced=newForced
        )

if splittedCommand[0] == 'mode':
    
    newState = splittedCommand[1] == 'on'
    if newState != device['forced']:
        db.saveCurrentDeviceStatus(
            deviceIdentifier,
            forced=newState
        )
        if not newState:
            deviceController.controlDevices(db, deviceIdentifier)

    print("Done changing the mode.")