#!/usr/bin/env python3

from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
import sys

IP_ADDRESS = sys.argv[1]

reader = ModbusTCPReader(IP_ADDRESS)

print(reader.readData(int(sys.argv[2]), int(sys.argv[3]), unit= int(sys.argv[4])))
