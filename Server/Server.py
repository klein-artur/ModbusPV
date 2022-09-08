#!/usr/bin/env python3

from Logger import log
from config import MODBUS_IP_ADDRESS
from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
from db.sqliteConnect import insertReading
import pathlib
from pathlib import Path
from ForecastReader import combinedForecasts, ForecastPlane
from time import time
from datetime import datetime
from DeviceController import controlDevices
import signal
import sys

PATH = pathlib.Path(__file__).parent.resolve()

log()
log("Server Started!")

print("starting now")

reader = ModbusDataReader(
    ModbusTCPReader(MODBUS_IP_ADDRESS)
)

print("connected")

def signal_handler(sig, frame):
    log('Server Stopped!')
    log()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

lastForecastRead = 0

while (True):
    try:
        print("")
        currentTime = int(time())

        forecast = None

        if currentTime - lastForecastRead > 9000:
            print("read forecast")
            log("Will read forecast.")
            try:
                forecast = combinedForecasts([
                                ForecastPlane("48.091284", "12.6368852", "17", "98", "22000"),
                                ForecastPlane("48.091284", "12.6368852", "30", "-82", "7900")
                            ])

                log("Forecast read.")

                lastForecastRead = currentTime
            except Exception as err:
                print(f"error reading forecast: {err}")
                log(f"error reading forecast: {err}")

        print("Last time forecast was read: " + datetime.utcfromtimestamp(lastForecastRead).strftime('%Y-%m-%d %H:%M:%S UTC'))

        print("Read Modbus")

        resultDict = reader.getPVDataSmoothed()

        print("Modbus read.")

        print("Done, write")

        if resultDict is not None:
            insertReading(resultDict, forecast)

        print("Control devices.")

        controlDevices()

    except Exception as err:
        print(f"error reading data: {err}")
        log(f"error reading data: {err}")
        reader = ModbusDataReader(
            ModbusTCPReader(MODBUS_IP_ADDRESS)
        )

#TODO: Disconnect!
