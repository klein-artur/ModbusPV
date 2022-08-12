from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Defaults

Defaults.RetryOnEmpty = True
Defaults.Timeout = 5
Defaults.Retries = 20

UNIT = 0x01

class ModbusTCPReader:

    def __init__(self, ip_address):
        self.client = ModbusTcpClient(ip_address)
        self.client.connect()

    def handleResult(self, data, length):
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

    def readData(self, register, len):
        while (True):
            rr = self.client.read_holding_registers(register, len, unit=UNIT)
            if not rr.isError():
                return self.handleResult(rr, len)

            else:
                # Handle Error.
                print(rr)

# TODO: Diconnect!
