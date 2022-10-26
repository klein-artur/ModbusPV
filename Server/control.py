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

device = list(filter(
    lambda device: device["identifier"] == deviceIdentifier, 
    deviceController.getDevices(db)
))[0]

if splittedCommand[0] == 'switch':

    newState = splittedCommand[1] == 'on'
    newForced = False if device['forced'] else True

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