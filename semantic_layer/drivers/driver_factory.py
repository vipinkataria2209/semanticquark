"""Driver factory for registration and discovery."""

from typing import Dict, Optional, Type, Union

from semantic_layer.drivers.base_driver import BaseDriver, ConnectionConfig
from semantic_layer.plugins.registry import get_plugin_registry


class DriverFactory:
    """Factory for creating and managing database drivers.
    
    This factory maintains backward compatibility while also supporting
    the new plugin system. Drivers can be registered either way.
    """
    
    _drivers: Dict[str, Type[BaseDriver]] = {}
    
    @classmethod
    def register(cls, name: str, driver_class: Type[BaseDriver]):
        """Register a driver class (legacy method, also registers in plugin system).
        
        Args:
            name: Driver name (e.g., 'postgres', 'mysql')
            driver_class: Driver class that extends BaseDriver
        """
        cls._drivers[name] = driver_class
        # Also register in plugin registry for unified plugin system
        try:
            from semantic_layer.plugins.registry import get_plugin_registry
            registry = get_plugin_registry()
            registry.register(driver_class)
        except Exception:
            # If plugin system not available, continue with legacy registration
            pass
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseDriver]]:
        """Get a driver class by name (legacy method).
        
        Args:
            name: Driver name
            
        Returns:
            Optional[Type[BaseDriver]]: Driver class or None if not found
        """
        return cls._drivers.get(name)
    
    @classmethod
    def list_drivers(cls) -> list[str]:
        """List all registered driver names (includes both legacy and plugin drivers).
        
        Returns:
            list[str]: List of available driver names
        """
        # Combine legacy and plugin registry
        legacy = list(cls._drivers.keys())
        try:
            registry = get_plugin_registry()
            plugins = registry.list_plugins("driver")
            plugin_names = [p["name"] for p in plugins.get("driver", [])]
            # Also check for aliases (postgresql -> postgres)
            all_names = set(legacy + plugin_names)
            return sorted(list(all_names))
        except Exception:
            return legacy
    
    @classmethod
    def create(cls, name: str, config: Union[ConnectionConfig, Dict]) -> BaseDriver:
        """Create a driver instance (enhanced to use plugin system with fallback).
        
        Args:
            name: Driver name (e.g., 'postgres', 'mysql')
            config: Connection configuration (ConnectionConfig or dict)
            
        Returns:
            BaseDriver: Initialized driver instance
            
        Raises:
            ValueError: If driver is not found
        """
        # Normalize config to dict if needed
        if isinstance(config, ConnectionConfig):
            config_dict = config.dict()
        else:
            config_dict = config
        
        # Try plugin registry first (new way)
        try:
            registry = get_plugin_registry()
            plugin = registry.load_plugin(
                plugin_type="driver",
                name=name,
                config=config_dict
            )
            # Convert back to ConnectionConfig for backward compatibility
            if isinstance(plugin, BaseDriver):
                if not hasattr(plugin, 'config') or plugin.config is None:
                    plugin.config = ConnectionConfig(**config_dict)
                return plugin
        except (ValueError, Exception):
            # Fallback to legacy registration
            pass
        
        # Fallback to legacy registration (backward compatibility)
        driver_class = cls.get(name)
        if not driver_class:
            available = cls.list_drivers()
            raise ValueError(
                f"Driver '{name}' not found. Available drivers: {available}"
            )
        
        # Create instance with ConnectionConfig
        if isinstance(config, ConnectionConfig):
            return driver_class(config)
        else:
            return driver_class(ConnectionConfig(**config))


# Auto-register built-in drivers
def _register_builtin_drivers():
    """Register built-in drivers (both legacy and plugin system)."""
    try:
        from semantic_layer.drivers.postgres_driver import PostgresDriver
        DriverFactory.register("postgresql", PostgresDriver)
        DriverFactory.register("postgres", PostgresDriver)
    except ImportError:
        pass
    
    try:
        from semantic_layer.drivers.mysql_driver import MySQLDriver
        DriverFactory.register("mysql", MySQLDriver)
    except ImportError:
        pass
    
    # Also load plugins via plugin loader
    try:
        from semantic_layer.plugins.loader import PluginLoader
        PluginLoader.load_built_in_plugins()
    except Exception:
        # If plugin system not available, continue with legacy registration
        pass


# Register on import
_register_builtin_drivers()

