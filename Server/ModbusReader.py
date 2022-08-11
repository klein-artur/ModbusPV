#!/usr/bin/env python3

import sched, time

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Defaults


Defaults.RetryOnEmpty = True
Defaults.Timeout = 5
Defaults.Retries = 20

UNIT = 0x01

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

    startTime = time.time()

    gridOutputValues = []
    pvActivePowerValues = []
    batteryChargeValues = []
    pvInputValues = []

    while(time.time() - startTime < 60):
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
    print("Battery: " + str(readData(37760, 1)))
    print("")
    print("Potential usage: " + str(averagePvInput - averageBatteryCharge - averageGridOutput))

# TODO: Disconnect!
