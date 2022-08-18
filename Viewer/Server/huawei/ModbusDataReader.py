from . import ModbusRegisters
from . import ModbusTCPReader
import collections

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
        return self.reader.readData(ModbusRegisters.PV_INPUT[0], ModbusRegisters.PV_INPUT[1]) / 1000

    def pvInputSmoothed(self):
        self.pvInputValues.append(self.pvInput())
        return average(self.pvInputValues)

    def batteryState(self):
        return self.reader.readData(ModbusRegisters.BATTERY_STATE[0], ModbusRegisters.BATTERY_STATE[1]) / 10

    def getPVDataSmoothed(self):
        averageGridOutput = self.gridOutputSmoothed()
        averageBatteryCharge = self.batteryChargeSmoothed()
        averagePVInput = self.pvInputSmoothed()

        batteryState = self.batteryState()

        return {
            "gridOutput": averageGridOutput,
            "batteryCharge": averageBatteryCharge,
            "batteryState": batteryState,
            "pvInput": averagePVInput,
            "timestamp": int(time())
        }