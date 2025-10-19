"""
Furcate Bridge - Base Protocol Adapter

Defines the interface for all protocol adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable
from datetime import datetime


class BaseAdapter(ABC):
    """Base class for all Furcate protocol adapters."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize adapter with configuration.
        
        Args:
            config: Adapter-specific configuration dictionary
        """
        self.config = config
        self.connected = False
        self.callbacks: Dict[str, Callable] = {}
        self._connection = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the device/network.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the device/network."""
        pass
    
    @abstractmethod
    def read(self, address: str) -> Optional[Any]:
        """Read data from a specific address/topic.
        
        Args:
            address: Protocol-specific address or topic
            
        Returns:
            Data read from the address, or None if failed
        """
        pass
    
    @abstractmethod
    def write(self, address: str, data: Any) -> bool:
        """Write data to a specific address/topic.
        
        Args:
            address: Protocol-specific address or topic
            data: Data to write
            
        Returns:
            True if write successful, False otherwise
        """
        pass
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for specific events.
        
        Args:
            event: Event name (e.g., 'on_data', 'on_connect')
            callback: Callable to execute on event
        """
        self.callbacks[event] = callback
    
    def trigger_callback(self, event: str, *args, **kwargs) -> None:
        """Trigger a registered callback.
        
        Args:
            event: Event name
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback
        """
        if event in self.callbacks:
            self.callbacks[event](*args, **kwargs)
    
    def is_connected(self) -> bool:
        """Check if adapter is connected.
        
        Returns:
            Connection status
        """
        return self.connected
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get adapter metadata.
        
        Returns:
            Dictionary with adapter information
        """
        return {
            'protocol': self.__class__.__name__.replace('Adapter', '').upper(),
            'connected': self.connected,
            'config': self.config
        }
