#!/usr/bin/env python3

from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
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

def writeStateFile(resultDict):

    jsonString = json.dumps(resultDict)

    with open(str(PATH) + "/state.json", "w") as outfile:
        outfile.write(jsonString)
        outfile.close()

def writeHistory(resultDict):
    currentTime = int(time.time())
    h24Before = currentTime - 86400
    resultDict['timestamp'] = int(time.time())

    fle = Path(str(PATH) + "/history.json")
    fle.touch(exist_ok=True)

    currentFileContent = ""
    with open(str(PATH) + "/history.json", "r") as file:
        currentFileContent = file.read()
        file.close()
        
    if not currentFileContent:
        currentFileContent = "[]"
    array = json.loads(currentFileContent)
    array.append(resultDict)

    array = [obj for obj in array if obj["timestamp"] >= h24Before]

    with open(str(PATH) + "/history.json", "w") as file:
        json.dump(array, file)
        file.close()


while (True):

    print("")
    print("Read")

    resultDict = reader.getPVDataSmoothed()

    print("Done, write")

    writeStateFile(resultDict)

    writeHistory(resultDict)

# TODO: Disconnect!
