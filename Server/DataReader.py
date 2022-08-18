#!/usr/bin/env python3

from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
from db.sqliteConnect import insertReading
import pathlib
from pathlib import Path
from ForecastReader import combinedForecasts, ForecastPlane
from time import time

PATH = pathlib.Path(__file__).parent.resolve()
IP_ADDRESS = "192.168.178.77"

print("starting now")

reader = ModbusDataReader(
    ModbusTCPReader(IP_ADDRESS)
)

print("connected")

lastForecastRead = 0

while (True):

    print("")
    print("Read Modbus")

    resultDict = reader.getPVDataSmoothed()

    print("Modbus read.")

    currentTime = time()

    forecast = None

    if currentTime - lastForecastRead > 360:
        print("read forecast")
        try:
            forecast = combinedForecasts([
                            ForecastPlane("48,05,28", "12,38,12", "17", "98", "21.6"),
                            ForecastPlane("48,05,28", "12,38,12", "30", "-82", "7.9")
                        ])
        except Exception as err:
            print(f"error reading forecast: {err}")
        lastForecastRead = currentTime

    print("Done, write")

    insertReading(resultDict, forecast)

#TODO: Disconnect!
