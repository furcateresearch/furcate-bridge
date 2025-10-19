#!/usr/bin/env python3
"""Furcate Bridge - Modbus PLC Reader Example"""

import time
import logging
from adapters.modbus import ModbusAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    config = {
        'type': 'tcp',
        'host': '192.168.1.100',
        'port': 502,
        'unit_id': 1
    }
    
    adapter = ModbusAdapter(config)
    
    if not adapter.connect():
        logger.error("Connection failed")
        return
    
    # Read sensor data from PLC
    for i in range(10):
        values = adapter.read_holding_registers(0, 5)
        if values:
            logger.info(f"PLC values: {values}")
        time.sleep(1)
    
    adapter.disconnect()


if __name__ == '__main__':
    main()
