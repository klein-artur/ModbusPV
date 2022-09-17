from . import ModbusRegisters
from . import ModbusTCPReader
import collections
from time import sleep

DEBUG = True

from time import time

def average(list):
    return sum(list) / len(list)

def max(a, b): 
    if a >= b:
        return a
    else:
        return b

def min(a, b): 
    if a <= b:
        return a
    else:
        return b

class ModbusDataReader:

    batteryChargeValues = collections.deque([], ModbusRegisters.MOVING_AVERAGE)
    gridOutputValues = collections.deque([], ModbusRegisters.MOVING_AVERAGE)
    pvInputValues = collections.deque([], ModbusRegisters.MOVING_AVERAGE)

    def __init__(self, reader: ModbusTCPReader):
        self.reader = reader

    def batteryCharge(self):
        return self.reader.readData(ModbusRegisters.BATTERY_CHARGE[0], ModbusRegisters.BATTERY_CHARGE[1]) / 1000

    def batteryChargeSmoothed(self):
        self.batteryChargeValues.append(self.batteryCharge())
        return average(self.batteryChargeValues)

    def gridOutput(self):
        return self.reader.readData(ModbusRegisters.GRID_OUTPUT[0], ModbusRegisters.GRID_OUTPUT[1]) / 1000

    def gridOutputSmoothed(self):
        self.gridOutputValues.append(self.gridOutput())
        return average(self.gridOutputValues)

    def pvInput(self):
        return (self.reader.readData(ModbusRegisters.PV_INPUT[0], ModbusRegisters.PV_INPUT[1], 0x01) + self.reader.readData(ModbusRegisters.PV_INPUT[0], ModbusRegisters.PV_INPUT[1], 0x02)) / 1000

    def pvInputSmoothed(self):
        self.pvInputValues.append(self.pvInput())
        return average(self.pvInputValues)

    def batteryState(self):
        return self.reader.readData(ModbusRegisters.BATTERY_STATE[0], ModbusRegisters.BATTERY_STATE[1]) / 10

    def accGridOutput(self):
        return self.reader.readData(ModbusRegisters.ACC_GRID_OUTPUT[0], ModbusRegisters.ACC_GRID_OUTPUT[1]) / 100

    def accGridInput(self):
        return self.reader.readData(ModbusRegisters.ACC_GRID_INPUT[0], ModbusRegisters.ACC_GRID_INPUT[1]) / 100

    def getPVDataSmoothed(self):

        if DEBUG:
            sleep(1.5)
            return {
                "gridOutput": -0.01,
                "batteryCharge": -2.0,
                "batteryState": 100,
                "pvInput": 0.0,
                "timestamp": int(time()),
                "accGridOutput": 421.02,
                "accGridInput": 47.5
            }

        averageGridOutput = self.gridOutputSmoothed()
        averageBatteryCharge = self.batteryChargeSmoothed()
        averagePVInput = self.pvInputSmoothed()

        if averageGridOutput > 30.0:
            return None

        batteryState = self.batteryState()

        accGridOutput = self.accGridOutput()
        accGridInput = self.accGridInput()

        return {
            "gridOutput": averageGridOutput,
            "batteryCharge": averageBatteryCharge,
            "batteryState": batteryState,
            "pvInput": averagePVInput,
            "timestamp": int(time()),
            "accGridOutput": accGridOutput,
            "accGridInput": accGridInput
        }