import pytest
from adapters.modbus import ModbusAdapter


def test_modbus_tcp_initialization():
    config = {
        'type': 'tcp',
        'host': '192.168.1.100',
        'port': 502
    }
    adapter = ModbusAdapter(config)
    assert adapter.modbus_type == 'tcp'
    assert not adapter.is_connected()


def test_modbus_rtu_initialization():
    config = {
        'type': 'rtu',
        'port': '/dev/ttyUSB0',
        'baudrate': 9600
    }
    adapter = ModbusAdapter(config)
    assert adapter.modbus_type == 'rtu'


def test_invalid_modbus_type():
    config = {'type': 'invalid'}
    with pytest.raises(ValueError):
        ModbusAdapter(config)
