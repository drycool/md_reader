"""
Dependency injection container for md_reader.

This module provides a simple but powerful dependency injection system
that enables loose coupling, better testability, and cleaner architecture.
"""

from typing import Dict, Type, Any, Optional, Callable, TypeVar, cast
from threading import Lock
import inspect

from .interfaces import IDependencyContainer
from .exceptions import ConfigurationError
from .logger import get_logger

logger = get_logger("container")

T = TypeVar('T')


class LifetimeScope:
    """Defines the lifetime of a dependency."""
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Single instance for container lifetime
    SCOPED = "scoped"        # Single instance per scope


class DependencyRegistration:
    """Represents a dependency registration."""
    
    def __init__(
        self, 
        interface: Type, 
        implementation: Optional[Type] = None,
        factory: Optional[Callable] = None,
        instance: Optional[Any] = None,
        lifetime: str = LifetimeScope.TRANSIENT
    ):
        self.interface = interface
        self.implementation = implementation
        self.factory = factory
        self.instance = instance
        self.lifetime = lifetime
        self.singleton_instance = None
        
    def create_instance(self, container: 'DependencyContainer') -> Any:
        """Create an instance based on registration type."""
        if self.instance is not None:
            return self.instance
        
        if self.lifetime == LifetimeScope.SINGLETON and self.singleton_instance is not None:
            return self.singleton_instance
        
        if self.factory is not None:
            instance = self.factory(container)
        elif self.implementation is not None:
            instance = container._create_instance(self.implementation)
        else:
            raise ConfigurationError(
                f"No implementation or factory registered for {self.interface.__name__}",
                f"Interface: {self.interface}"
            )
        
        if self.lifetime == LifetimeScope.SINGLETON:
            self.singleton_instance = instance
        
        return instance


class DependencyContainer:
    """Simple dependency injection container."""
    
    def __init__(self, parent: Optional['DependencyContainer'] = None):
        self._registrations: Dict[Type, DependencyRegistration] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._parent = parent
        self._lock = Lock()
        logger.debug("Dependency container created")
    
    def register(
        self, 
        interface: Type[T], 
        implementation: Type[T], 
        lifetime: str = LifetimeScope.TRANSIENT
    ) -> 'DependencyContainer':
        """
        Register an implementation for an interface.
        
        Args:
            interface: The interface type
            implementation: The implementation type
            lifetime: The lifetime scope for the dependency
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            if not issubclass(implementation, interface) and not self._implements_protocol(implementation, interface):
                raise ConfigurationError(
                    f"Implementation {implementation.__name__} does not implement {interface.__name__}",
                    f"Interface: {interface}, Implementation: {implementation}"
                )
            
            registration = DependencyRegistration(
                interface=interface,
                implementation=implementation,
                lifetime=lifetime
            )
            
            self._registrations[interface] = registration
            logger.debug(f"Registered {implementation.__name__} for {interface.__name__} with {lifetime} lifetime")
            
        return self
    
    def register_factory(
        self, 
        interface: Type[T], 
        factory: Callable[['DependencyContainer'], T],
        lifetime: str = LifetimeScope.TRANSIENT
    ) -> 'DependencyContainer':
        """
        Register a factory function for an interface.
        
        Args:
            interface: The interface type
            factory: Factory function that takes container and returns instance
            lifetime: The lifetime scope for the dependency
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            registration = DependencyRegistration(
                interface=interface,
                factory=factory,
                lifetime=lifetime
            )
            
            self._registrations[interface] = registration
            logger.debug(f"Registered factory for {interface.__name__} with {lifetime} lifetime")
            
        return self
    
    def register_instance(
        self, 
        interface: Type[T], 
        instance: T
    ) -> 'DependencyContainer':
        """
        Register a specific instance for an interface.
        
        Args:
            interface: The interface type
            instance: The instance to register
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            registration = DependencyRegistration(
                interface=interface,
                instance=instance,
                lifetime=LifetimeScope.SINGLETON
            )
            
            self._registrations[interface] = registration
            logger.debug(f"Registered instance for {interface.__name__}")
            
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve an implementation for an interface.
        
        Args:
            interface: The interface type to resolve
            
        Returns:
            An instance of the implementation
            
        Raises:
            ConfigurationError: If no registration found
        """
        with self._lock:
            registration = self._get_registration(interface)
            
            if registration.lifetime == LifetimeScope.SCOPED:
                # Check if we already have a scoped instance
                if interface in self._scoped_instances:
                    return cast(T, self._scoped_instances[interface])
                
                # Create new scoped instance
                instance = registration.create_instance(self)
                self._scoped_instances[interface] = instance
                return cast(T, instance)
            
            return cast(T, registration.create_instance(self))
    
    def try_resolve(self, interface: Type[T]) -> Optional[T]:
        """
        Try to resolve an interface, returning None if not found.
        
        Args:
            interface: The interface type to resolve
            
        Returns:
            An instance or None if not registered
        """
        try:
            return self.resolve(interface)
        except ConfigurationError:
            return None
    
    def is_registered(self, interface: Type) -> bool:
        """Check if an interface is registered."""
        return (interface in self._registrations) or \
               (self._parent is not None and self._parent.is_registered(interface))
    
    def create_scope(self) -> 'DependencyContainer':
        """
        Create a new dependency scope.
        
        Returns:
            A new container with this container as parent
        """
        return DependencyContainer(parent=self)
    
    def dispose_scope(self) -> None:
        """Dispose the current scope, clearing scoped instances."""
        with self._lock:
            # Dispose any disposable scoped instances
            for instance in self._scoped_instances.values():
                if hasattr(instance, 'dispose'):
                    try:
                        instance.dispose()
                    except Exception as e:
                        logger.warning(f"Error disposing instance: {e}")
            
            self._scoped_instances.clear()
            logger.debug("Scope disposed")
    
    def get_registrations(self) -> Dict[Type, DependencyRegistration]:
        """Get all registrations (for debugging/testing)."""
        return self._registrations.copy()
    
    def _get_registration(self, interface: Type) -> DependencyRegistration:
        """Get registration for interface, checking parent if needed."""
        if interface in self._registrations:
            return self._registrations[interface]
        
        if self._parent is not None:
            return self._parent._get_registration(interface)
        
        raise ConfigurationError(
            f"No registration found for {interface.__name__}",
            f"Available registrations: {list(self._registrations.keys())}"
        )
    
    def _create_instance(self, implementation: Type) -> Any:
        """Create instance with dependency injection."""
        constructor = implementation.__init__
        sig = inspect.signature(constructor)
        
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                if param.default == inspect.Parameter.empty:
                    raise ConfigurationError(
                        f"Cannot inject parameter '{param_name}' in {implementation.__name__}",
                        "Parameter has no type annotation and no default value"
                    )
                continue
            
            try:
                kwargs[param_name] = self.resolve(param_type)
            except ConfigurationError:
                if param.default != inspect.Parameter.empty:
                    # Parameter has default value, skip injection
                    continue
                else:
                    raise ConfigurationError(
                        f"Cannot inject parameter '{param_name}' of type {param_type.__name__} in {implementation.__name__}",
                        f"No registration found for {param_type.__name__}"
                    )
        
        try:
            return implementation(**kwargs)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create instance of {implementation.__name__}",
                f"Error: {str(e)}"
            )
    
    def _implements_protocol(self, implementation: Type, interface: Type) -> bool:
        """Check if implementation satisfies protocol interface."""
        if not hasattr(interface, '__protocol__'):
            return False
        
        # Simple protocol checking - verify required methods exist
        if hasattr(interface, '__annotations__'):
            for attr_name in interface.__annotations__:
                if not hasattr(implementation, attr_name):
                    return False
        
        # Check for callable attributes (methods)
        for attr_name in dir(interface):
            if not attr_name.startswith('_'):
                interface_attr = getattr(interface, attr_name, None)
                if callable(interface_attr):
                    if not hasattr(implementation, attr_name):
                        return False
                    impl_attr = getattr(implementation, attr_name)
                    if not callable(impl_attr):
                        return False
        
        return True


# Global container instance
_global_container: Optional[DependencyContainer] = None
_container_lock = Lock()


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _global_container
    
    if _global_container is None:
        with _container_lock:
            if _global_container is None:
                _global_container = DependencyContainer()
                logger.info("Global dependency container created")
    
    return _global_container


def set_container(container: DependencyContainer) -> None:
    """Set the global dependency container."""
    global _global_container
    with _container_lock:
        _global_container = container
        logger.info("Global dependency container replaced")


def reset_container() -> None:
    """Reset the global dependency container."""
    global _global_container
    with _container_lock:
        if _global_container is not None:
            _global_container.dispose_scope()
        _global_container = None
        logger.info("Global dependency container reset")


# Decorators for dependency injection

def injectable(interface: Type):
    """Decorator to mark a class as injectable for an interface."""
    def decorator(cls):
        # Auto-register with global container
        container = get_container()
        container.register(interface, cls)
        return cls
    return decorator


def singleton(interface: Type):
    """Decorator to mark a class as singleton for an interface."""
    def decorator(cls):
        # Auto-register as singleton with global container
        container = get_container()
        container.register(interface, cls, LifetimeScope.SINGLETON)
        return cls
    return decorator


# Context manager for scoped dependencies

class dependency_scope:
    """Context manager for dependency scoping."""
    
    def __init__(self, container: Optional[DependencyContainer] = None):
        self.container = container or get_container()
        self.scope: Optional[DependencyContainer] = None
    
    def __enter__(self) -> DependencyContainer:
        self.scope = self.container.create_scope()
        return self.scope
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.scope:
            self.scope.dispose_scope()


# Utility functions

def configure_default_dependencies() -> DependencyContainer:
    """Configure default dependencies for the application."""
    from .loader import MarkdownLoader
    from .toc import TocBuilder
    from .viewer import InteractiveViewer
    from .validators import PathValidator, InputValidator
    from .interfaces import IFileLoader, ITOCBuilder, IViewer, IValidator
    
    container = get_container()
    
    # Register default implementations
    container.register(IFileLoader, MarkdownLoader, LifetimeScope.SINGLETON)
    container.register(ITOCBuilder, TocBuilder, LifetimeScope.SINGLETON)
    container.register(IViewer, InteractiveViewer, LifetimeScope.TRANSIENT)
    
    logger.info("Default dependencies configured")
    return container