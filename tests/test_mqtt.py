import pytest
from adapters.mqtt import MQTTAdapter, create_mqtt_config


def test_mqtt_config_creation():
    config = create_mqtt_config(
        broker='test.mosquitto.org',
        port=1883,
        username='test'
    )
    assert config['broker'] == 'test.mosquitto.org'
    assert config['port'] == 1883
    assert config['username'] == 'test'
    assert 'client_id' in config


def test_mqtt_adapter_initialization():
    config = create_mqtt_config(broker='localhost')
    adapter = MQTTAdapter(config)
    assert adapter.broker == 'localhost'
    assert not adapter.is_connected()


def test_mqtt_callbacks():
    config = create_mqtt_config(broker='localhost')
    adapter = MQTTAdapter(config)
    
    called = []
    adapter.register_callback('test_event', lambda: called.append(1))
    adapter.trigger_callback('test_event')
    
    assert len(called) == 1
