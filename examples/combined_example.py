#!/usr/bin/env python3
"""Furcate Bridge - Combined MQTT + Modbus Example

Reads from Modbus PLC and publishes to MQTT.
"""

import time
import logging
from adapters.mqtt import MQTTAdapter, create_mqtt_config
from adapters.modbus import ModbusAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Setup MQTT
    mqtt_config = create_mqtt_config(
        broker='test.mosquitto.org',
        client_id='furcate-plc-bridge'
    )
    mqtt = MQTTAdapter(mqtt_config)
    mqtt.connect()
    
    # Setup Modbus
    modbus_config = {
        'type': 'tcp',
        'host': '192.168.1.100',
        'port': 502
    }
    modbus = ModbusAdapter(modbus_config)
    modbus.connect()
    
    # Read from PLC, publish to MQTT
    for i in range(10):
        values = modbus.read_holding_registers(0, 4)
        if values:
            data = {
                'temperature': values[0] / 10.0,
                'pressure': values[1],
                'status': values[2],
                'timestamp': time.time()
            }
            mqtt.write('factory/plc-001/data', data)
            logger.info(f"Published: {data}")
        time.sleep(2)
    
    modbus.disconnect()
    mqtt.disconnect()


if __name__ == '__main__':
    main()
