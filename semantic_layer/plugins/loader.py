"""Plugin loader for discovering and loading plugins."""

import importlib
import importlib.util
import pkgutil
from pathlib import Path
from typing import Optional
from semantic_layer.plugins.base import PluginInterface
from semantic_layer.plugins.registry import get_plugin_registry


class PluginLoader:
    """Discover and load plugins from packages."""
    
    @staticmethod
    def load_built_in_plugins() -> None:
        """Load all built-in plugins from SemanticQuark packages."""
        registry = get_plugin_registry()
        
        # Load driver plugins
        PluginLoader._load_plugins_from_package("semantic_layer.drivers")
        
        # Load cache plugins
        PluginLoader._load_plugins_from_package("semantic_layer.cache")
        
        # Load auth plugins
        PluginLoader._load_plugins_from_package("semantic_layer.auth")
    
    @staticmethod
    def load_external_plugins(plugin_directory: str) -> None:
        """Load plugins from external directory.
        
        Args:
            plugin_directory: Path to directory containing plugin modules
        """
        registry = get_plugin_registry()
        plugin_path = Path(plugin_directory)
        
        if not plugin_path.exists():
            return
        
        if not plugin_path.is_dir():
            return
        
        # Add directory to Python path temporarily
        import sys
        sys.path.insert(0, str(plugin_path.parent))
        
        try:
            for finder, module_name, ispkg in pkgutil.iter_modules([str(plugin_path)]):
                if ispkg:
                    continue
                
                try:
                    spec = finder.find_spec(module_name)
                    if spec is None or spec.loader is None:
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find PluginInterface subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        if (isinstance(attr, type) and
                            issubclass(attr, PluginInterface) and
                            attr is not PluginInterface):
                            
                            try:
                                registry.register(attr)
                            except Exception as e:
                                # Log but don't fail
                                pass
                
                except Exception:
                    # Skip modules that can't be loaded
                    pass
        finally:
            # Remove from path
            if str(plugin_path.parent) in sys.path:
                sys.path.remove(str(plugin_path.parent))
    
    @staticmethod
    def _load_plugins_from_package(package_name: str) -> None:
        """Load all plugins from a package.
        
        Args:
            package_name: Full package name (e.g., 'semantic_layer.drivers')
        """
        registry = get_plugin_registry()
        
        try:
            package = importlib.import_module(package_name)
            if not hasattr(package, '__path__'):
                return
            
            package_path = package.__path__
            
            for finder, module_name, ispkg in pkgutil.iter_modules(package_path):
                if ispkg:
                    # Recursively load from subpackages
                    full_module_name = f"{package_name}.{module_name}"
                    PluginLoader._load_plugins_from_package(full_module_name)
                    continue
                
                try:
                    full_module_name = f"{package_name}.{module_name}"
                    module = importlib.import_module(full_module_name)
                    
                    # Find PluginInterface subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        if (isinstance(attr, type) and
                            issubclass(attr, PluginInterface) and
                            attr is not PluginInterface):
                            
                            try:
                                registry.register(attr)
                            except Exception as e:
                                # Log but don't fail on registration errors
                                pass
                
                except Exception:
                    # Skip modules that can't be loaded
                    pass
        
        except ImportError:
            # Package doesn't exist, skip
            pass

