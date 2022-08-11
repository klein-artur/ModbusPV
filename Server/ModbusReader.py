#!/usr/bin/env python3

import collections
import sched, time
import json 
import pathlib

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Defaults


Defaults.RetryOnEmpty = True
Defaults.Timeout = 5
Defaults.Retries = 20

UNIT = 0x01
PATH = pathlib.Path(__file__).parent.resolve()
MOVING_AVERAGE = 2


gridOutputValues = collections.deque([], MOVING_AVERAGE)
pvActivePowerValues = collections.deque([], MOVING_AVERAGE)
batteryChargeValues = collections.deque([], MOVING_AVERAGE)
pvInputValues = collections.deque([], MOVING_AVERAGE)


print(PATH)

print("starting now")

client = ModbusTcpClient('192.168.178.77')
client.connect()

def handleResult(data, length):
    result = 0
    for item in range(length):
        result |= data.registers[item] << ((length - 1 - item) * 16)

    signBit = 1 << (length * 16 - 1)
    signBitSet = result & signBit > 0

    if signBitSet:
        allSetBits = 0
        for bit in reversed(range(length * 16 - 1)):
            allSetBits |= 1 << bit

        result ^= signBit

        result ^= allSetBits

        result *= -1

    return result

def readData(register, len):
    while (True):
        rr = client.read_holding_registers(register, len, unit=UNIT)
        if not rr.isError():
            return handleResult(rr, len)

        else:
            # Handle Error.
            print(rr)


print("connected")

def average(list):
    return sum(list) / len(list)

def getAllData():
    gridOutputValues.append(readData(37113, 2))
    pvActivePowerValues.append(readData(32080, 2))
    batteryChargeValues.append(readData(37765, 2))
    pvInputValues.append(readData(32064, 2))

while (True):

    getAllData()

    # s = sched.scheduler(time.time, time.sleep)
    # def do_something(sc):
    #     getAllData()
    #     currentTime = time.time()
    #     if currentTime - startTime < 10:
    #         s.enter(1, 1, do_something, (sc,))
    # s.enter(1, 1, do_something, (s,))
    # s.run()

    print("")
    print("Data: ")

    averageGridOutput = average(gridOutputValues)
    averagePActivePower = average(pvActivePowerValues)
    averageBatteryCharge = average(batteryChargeValues)
    averagePvInput = average(pvInputValues)
    print("Grid output: " + str(averageGridOutput))
    print("PV Active Power: " + str(averagePActivePower))
    print("battery Charche: " + str(averageBatteryCharge))
    print("PV Input Power: " + str(averagePvInput))

    batteryState = readData(37760, 1)

    print("Battery: " + str(batteryState))
    print("")
    print("Potential usage: " + str(averagePvInput - averageBatteryCharge - averageGridOutput))

    resultDict = {
        "pvInput": averagePvInput / 1000,
        "gridOutput": averageGridOutput / 1000,
        "batteryCharge": averageBatteryCharge / 1000,
        "batteryState": batteryState / 10
    }

    with open(str(PATH) + "/state.json", "w") as outfile:
        json.dump(resultDict, outfile)

# TODO: Disconnect!
