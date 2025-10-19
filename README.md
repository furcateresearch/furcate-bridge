# Furcate Bridge

Protocol adapters for integrating Furcate distributed machine learning with existing industrial and IoT infrastructure.

## Features

- **MQTT Adapter**: Full MQTT 3.1.1/5.0 support with TLS
- **Modbus Adapter**: Modbus TCP and RTU for industrial PLCs
- **Extensible**: Easy to add custom protocol adapters
- **Production-Ready**: Robust error handling, logging, reconnection

## Installation

```bash
pip install furcate-bridge
```

## Quick Start

### MQTT Example

```python
from adapters.mqtt import MQTTAdapter, create_mqtt_config

# Configure
config = create_mqtt_config(
    broker='mqtt.example.com',
    port=1883,
    username='device',
    password='secret'
)

# Create adapter
adapter = MQTTAdapter(config)
adapter.connect()

# Subscribe to sensor data
def on_sensor_data(topic, data):
    print(f"Received: {data}")

adapter.subscribe('sensors/#', on_sensor_data)

# Publish inference results
adapter.write('results/device-001', {'prediction': 'normal'})
```

### Modbus Example

```python
from adapters.modbus import ModbusAdapter

# Configure for Modbus TCP
config = {
    'type': 'tcp',
    'host': '192.168.1.100',
    'port': 502,
    'unit_id': 1
}

adapter = ModbusAdapter(config)
adapter.connect()

# Read PLC data
values = adapter.read_holding_registers(address=0, count=10)
print(f"Register values: {values}")

# Write control signal
adapter.write_coil(address=0, value=True)
```

## Supported Protocols

| Protocol | Status | Use Cases |
|----------|--------|-----------|
| MQTT | ✅ Production | IoT sensors, smart devices |
| Modbus | ✅ Production | PLCs, industrial equipment |
| OPC-UA | 🚧 Planned | Factory automation |
| LoRaWAN | 🚧 Planned | Long-range IoT |

## Architecture

```
Application Layer (Your ML Code)
         ↓
    Furcate Bridge (Protocol Adapters)
         ↓
Legacy Systems (MQTT, Modbus, etc.)
```

## Custom Adapters

Create custom adapters by inheriting from `BaseAdapter`:

```python
from adapters.base import BaseAdapter

class CustomAdapter(BaseAdapter):
    def connect(self) -> bool:
        # Implementation
        pass
    
    def read(self, address: str):
        # Implementation
        pass
    
    def write(self, address: str, data):
        # Implementation
        pass
```

## Testing

```bash
pytest tests/
```

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please see CONTRIBUTING.md

## Support

- GitHub Issues: https://github.com/furcateresearch/furcate-bridge/issues
- Email: contact@furcate.io
