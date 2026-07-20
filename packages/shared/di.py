"""Dependency Injection Container for VisionForge"""

from typing import Dict, Any, Type, TypeVar, Callable, Optional
from functools import wraps
import inspect

T = TypeVar('T')


class ServiceContainer:
    """Lightweight Dependency Injection Container"""
    
    def __init__(self):
        self._services: Dict[str, Type] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register(self, name: str, service_type: Type[T], singleton: bool = False) -> None:
        """Register a service or factory
        
        Args:
            name: Service identifier
            service_type: Class to instantiate
            singleton: If True, reuse same instance
        """
        self._services[name] = service_type
        if singleton:
            self._singletons[name] = None
    
    def register_factory(self, name: str, factory: Callable, singleton: bool = False) -> None:
        """Register a factory function
        
        Args:
            name: Service identifier
            factory: Function that creates the service
            singleton: If True, reuse same instance
        """
        self._factories[name] = factory
        if singleton:
            self._singletons[name] = None
    
    def get(self, name: str) -> Any:
        """Get service instance
        
        Args:
            name: Service identifier
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not registered
        """
        # Check singleton cache first
        if name in self._singletons and self._singletons[name] is not None:
            return self._singletons[name]
        
        # Create instance from factory or class
        instance = None
        if name in self._factories:
            instance = self._factories[name]()
        elif name in self._services:
            service_type = self._services[name]
            instance = service_type()
        else:
            raise KeyError(f"Service '{name}' not registered")
        
        # Cache singleton
        if name in self._singletons:
            self._singletons[name] = instance
        
        return instance
    
    def clear(self) -> None:
        """Clear all registered services and singletons"""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()


# Global container instance
_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get global DI container"""
    return _container


def inject(**dependencies):
    """Dependency injection decorator
    
    Usage:
        @inject(db='database', llm='llm_provider')
        async def my_function(db, llm):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Inject dependencies from container
            for param_name, service_name in dependencies.items():
                if param_name not in kwargs:
                    kwargs[param_name] = _container.get(service_name)
            return func(*args, **kwargs)
        return wrapper
    
    return decorator
