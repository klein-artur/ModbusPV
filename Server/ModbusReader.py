#!/usr/bin/env python3

from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
from db.sqliteConnect import insertReading
import json 
import pathlib
import time
from pathlib import Path

PATH = pathlib.Path(__file__).parent.resolve()
IP_ADDRESS = "192.168.178.77"

print("starting now")

reader = ModbusDataReader(
    ModbusTCPReader(IP_ADDRESS)
)

print("connected")


while (True):

    print("")
    print("Read")

    resultDict = reader.getPVDataSmoothed()

    print("Done, write")

    insertReading(resultDict)

# TODO: Disconnect!
