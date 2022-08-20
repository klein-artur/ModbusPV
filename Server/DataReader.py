#!/usr/bin/env python3

from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
from db.sqliteConnect import insertReading
import pathlib
from pathlib import Path
from ForecastReader import combinedForecasts, ForecastPlane
from time import time
from datetime import datetime

PATH = pathlib.Path(__file__).parent.resolve()
IP_ADDRESS = "192.168.178.77"

print("starting now")

reader = ModbusDataReader(
    ModbusTCPReader(IP_ADDRESS)
)

print("connected")

lastForecastRead = 0

while (True):
    try:
        print("")
        currentTime = int(time())

        forecast = None

        if currentTime - lastForecastRead > 9000:
            print("read forecast")
            try:
                forecast = combinedForecasts([
                                ForecastPlane("48.091284", "12.6368852", "17", "98", "22000"),
                                ForecastPlane("48.091284", "12.6368852", "30", "-82", "7900")
                            ])
            except Exception as err:
                print(f"error reading forecast: {err}")
            lastForecastRead = currentTime

        print("Last time forecast read: " + datetime.utcfromtimestamp(lastForecastRead).strftime('%Y-%m-%d %H:%M:%S'))

        print("Read Modbus")

        resultDict = reader.getPVDataSmoothed()

        print("Modbus read.")

        print("Done, write")

        if resultDict is not None:
            insertReading(resultDict, forecast)

    except Exception as err:
        print(f"error reading data: {err}")
        reader = ModbusDataReader(
            ModbusTCPReader(IP_ADDRESS)
        )

#TODO: Disconnect!
