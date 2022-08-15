#!/usr/bin/env python3

from huawei.ModbusTCPReader import ModbusTCPReader
from huawei.ModbusDataReader import ModbusDataReader
import sys

IP_ADDRESS = "192.168.178.77"

reader = ModbusTCPReader(IP_ADDRESS)

print(reader.readData(int(sys.argv[1]), int(sys.argv[2])))
