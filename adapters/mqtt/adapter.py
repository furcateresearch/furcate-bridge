"""
Furcate Bridge - MQTT Protocol Adapter

Production-ready MQTT adapter using paho-mqtt 2.x for industrial IoT integration.
"""

import json
import logging
from typing import Any, Dict, Optional, Callable
import paho.mqtt.client as mqtt
from .base import BaseAdapter


logger = logging.getLogger(__name__)


class MQTTAdapter(BaseAdapter):
    """MQTT Protocol Adapter for Furcate Edge Devices.
    
    Supports MQTT 3.1.1 and 5.0 with TLS encryption and automatic reconnection.
    
    Example:
        config = {
            'broker': 'mqtt.example.com',
            'port': 1883,
            'client_id': 'furcate-device-001',
            'username': 'device',
            'password': 'secret',
            'tls': False
        }
        adapter = MQTTAdapter(config)
        adapter.connect()
        adapter.subscribe('sensors/#', lambda msg: print(msg.payload))
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize MQTT adapter.
        
        Args:
            config: Configuration dict with broker, port, credentials, etc.
        """
        super().__init__(config)
        
        self.broker = config.get('broker', 'localhost')
        self.port = config.get('port', 1883)
        self.client_id = config.get('client_id', 'furcate-mqtt-client')
        self.username = config.get('username')
        self.password = config.get('password')
        self.use_tls = config.get('tls', False)
        self.keepalive = config.get('keepalive', 60)
        
        # Initialize MQTT client (paho-mqtt 2.x)
        self.client = mqtt.Client(
            client_id=self.client_id,
            protocol=mqtt.MQTTv5 if config.get('mqtt_version', 5) == 5 else mqtt.MQTTv311
        )
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        # Set credentials if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Configure TLS if needed
        if self.use_tls:
            self.client.tls_set()
        
        self.subscriptions: Dict[str, Callable] = {}
        
    def connect(self) -> bool:
        """Connect to MQTT broker.
        
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to MQTT broker {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, self.keepalive)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        logger.info("Disconnecting from MQTT broker")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def read(self, topic: str) -> Optional[Any]:
        """Not applicable for MQTT (subscription-based).
        
        Use subscribe() instead for asynchronous message reception.
        """
        raise NotImplementedError("MQTT uses subscribe() for reading messages")
    
    def write(self, topic: str, data: Any) -> bool:
        """Publish data to MQTT topic.
        
        Args:
            topic: MQTT topic to publish to
            data: Data to publish (will be JSON-encoded if dict/list)
        
        Returns:
            True if publish successful
        """
        try:
            payload = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            result = self.client.publish(topic, payload, qos=1)
            result.wait_for_publish()
            logger.debug(f"Published to {topic}: {payload[:100]}")
            return result.is_published()
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False
    
    def subscribe(self, topic: str, callback: Optional[Callable] = None) -> bool:
        """Subscribe to MQTT topic.
        
        Args:
            topic: MQTT topic (supports wildcards: +, #)
            callback: Optional callback for messages on this topic
        
        Returns:
            True if subscription successful
        """
        try:
            self.client.subscribe(topic, qos=1)
            if callback:
                self.subscriptions[topic] = callback
            logger.info(f"Subscribed to topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to {topic}: {e}")
            return False
    
    def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from MQTT topic.
        
        Args:
            topic: MQTT topic to unsubscribe from
        
        Returns:
            True if unsubscribe successful
        """
        try:
            self.client.unsubscribe(topic)
            if topic in self.subscriptions:
                del self.subscriptions[topic]
            logger.info(f"Unsubscribed from topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {topic}: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback when connected to broker."""
        if reason_code == 0:
            self.connected = True
            logger.info("Successfully connected to MQTT broker")
            self.trigger_callback('on_connect')
        else:
            logger.error(f"Connection failed with code: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        """Callback when disconnected from broker."""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")
        self.trigger_callback('on_disconnect')
    
    def _on_message(self, client, userdata, message):
        """Callback when message received."""
        logger.debug(f"Received message on {message.topic}")
        
        # Try to parse as JSON
        try:
            payload = json.loads(message.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = message.payload
        
        # Call topic-specific callback if registered
        for topic_pattern, callback in self.subscriptions.items():
            if mqtt.topic_matches_sub(topic_pattern, message.topic):
                callback(message.topic, payload)
        
        # Trigger general callback
        self.trigger_callback('on_message', message.topic, payload)
    
    def _on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        """Callback when message published."""
        logger.debug(f"Message published: {mid}")
        self.trigger_callback('on_publish', mid)


# Configuration helper
def create_mqtt_config(
    broker: str,
    port: int = 1883,
    client_id: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    tls: bool = False
) -> Dict[str, Any]:
    """Create MQTT adapter configuration.
    
    Args:
        broker: MQTT broker hostname or IP
        port: MQTT broker port (default: 1883)
        client_id: MQTT client ID (auto-generated if None)
        username: Authentication username
        password: Authentication password
        tls: Enable TLS/SSL encryption
    
    Returns:
        Configuration dictionary
    """
    import uuid
    
    return {
        'broker': broker,
        'port': port,
        'client_id': client_id or f'furcate-{uuid.uuid4().hex[:8]}',
        'username': username,
        'password': password,
        'tls': tls
    }
