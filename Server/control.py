#!/usr/bin/env python3
import os
from Logger import log

import sys

from devices.DeviceController import DeviceController
from db.mysqlConnect import MySqlConnector

log('')
log('')
log(f"Begin controlling device.")
deviceIdentifier = sys.argv[1]
command = sys.argv[2]
log(f'Controlling the device "{deviceIdentifier}", command is "{command}"')

splittedCommand = command.split('=')

log(f'Initializing the device controller')
deviceController = DeviceController()
log(f'Device controller initialized. Now initializing the database')
db = MySqlConnector()

log(f'Database initialized. Getting the device status for the device from the database.')

device = db.getCurrentDeviceStatus(deviceIdentifier);

log(f'Got device from database. Will now get the config.')

deviceConfig = list(
    filter(
        lambda config: config['identifier'] == deviceIdentifier,
        deviceController.readDevicesFromConfigFile()
    )
)[0]
device.update(deviceConfig)

log(f'Config is loaded. Now will try to control the device.')

if splittedCommand[0] == 'switch':

    log(f'It is a switch action. So let´s switch the device')

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

    log(f'Device switched. Done.')

if splittedCommand[0] == 'mode':

    log(f'It is a mode action. So let´s switch the mode of the device')
    
    newState = splittedCommand[1] == 'on'
    if newState != device['forced']:
        db.saveCurrentDeviceStatus(
            deviceIdentifier,
            forced=newState
        )

    log(f'Done switched.')
    log('')
    log('')

    print("Done changing the mode.")