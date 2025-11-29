"""Driver factory for registration and discovery."""

from typing import Dict, Optional, Type

from semantic_layer.drivers.base_driver import BaseDriver


class DriverFactory:
    """Factory for creating and managing database drivers."""
    
    _drivers: Dict[str, Type[BaseDriver]] = {}
    
    @classmethod
    def register(cls, name: str, driver_class: Type[BaseDriver]):
        """Register a driver class."""
        cls._drivers[name] = driver_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseDriver]]:
        """Get a driver class by name."""
        return cls._drivers.get(name)
    
    @classmethod
    def list_drivers(cls) -> list[str]:
        """List all registered driver names."""
        return list(cls._drivers.keys())
    
    @classmethod
    def create(cls, name: str, config) -> BaseDriver:
        """Create a driver instance."""
        driver_class = cls.get(name)
        if not driver_class:
            raise ValueError(f"Driver '{name}' not found. Available: {cls.list_drivers()}")
        return driver_class(config)


# Auto-register built-in drivers
def _register_builtin_drivers():
    """Register built-in drivers."""
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


# Register on import
_register_builtin_drivers()

