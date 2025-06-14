# taskbuddy_project/core/dependency_container.py

import inspect
import logging # Still needed for logging its own operations if not using loguru for self_logger
import importlib
from typing import get_origin, get_args, Optional

# Loguru will now be the global logger.
from loguru import logger

# Import the loguru setup to ensure it's configured
import config.loguru_setup

class DependencyContainer:
    """
    A simple Inversion of Control (IoC) container for managing dependencies.
    Allows for registering concrete implementations for interfaces/abstractions
    and resolving them. Loggers are now globally available via Loguru.
    """
    def __init__(self):
        self._registrations = {} # Stores interface -> concrete_class_path mappings
        logger.debug("DEBUG - DependencyContainer initialized.")

    def register(self, abstraction: type, concrete_implementation_path: str):
        """
        Registers a concrete implementation for a given abstraction (interface or base class)
        by its full import path string. Handles generic types in abstraction.
        """
        # When registering, we often register a generic form (e.g., ICrudRepository[Task])
        # or a specific interface like ITaskRepository.
        # The key in _registrations should reflect this.
        
        # Determine the base abstraction for issubclass check
        # If ICrudRepository[Task], base_abstraction_for_check is ICrudRepository
        base_abstraction_for_check = get_origin(abstraction) if get_origin(abstraction) else abstraction

        try:
            module_path, class_name = concrete_implementation_path.rsplit('.', 1)
            concrete_module = importlib.import_module(module_path)
            concrete_implementation = getattr(concrete_module, class_name)
        except (ImportError, AttributeError, ValueError) as e:
            raise ValueError(
                f"ERROR - Failed to load concrete implementation '{concrete_implementation_path}'. "
                f"Please check the path. Error: {e}"
            ) from e

        # Validate that the concrete implementation is a subclass of the base abstraction.
        # E.g., CsvTaskRepository must be a subclass of ITaskRepository.
        if not issubclass(concrete_implementation, base_abstraction_for_check):
            raise ValueError(f"ERROR - Concrete implementation {concrete_implementation.__name__} "
                             f"does not implement abstraction {base_abstraction_for_check.__name__}.")

        # Register using the full abstraction (e.g., ITaskRepository or ICrudRepository[Task])
        self._registrations[abstraction] = concrete_implementation_path
        logger.debug(f"DEBUG - Registered {concrete_implementation.__name__} for {str(abstraction)}")


    def resolve(self, abstraction: type):
        """
        Resolves and returns an instance of the concrete implementation
        registered for the given abstraction. Handles nested dependencies recursively.
        """
        # For resolution, we first try to find an exact registration (e.g., for ITaskRepository).
        # If not found, and it's a generic type (e.g., ICrudRepository[Task]),
        # we then try to find a registration for its origin (ICrudRepository).
        
        concrete_implementation_path = self._registrations.get(abstraction)
        if not concrete_implementation_path and get_origin(abstraction):
            concrete_implementation_path = self._registrations.get(get_origin(abstraction))

        concrete_class = None
        if concrete_implementation_path:
            try:
                module_path, class_name = concrete_implementation_path.rsplit('.', 1)
                concrete_module = importlib.import_module(module_path)
                concrete_class = getattr(concrete_module, class_name)
            except (ImportError, AttributeError) as e:
                raise ValueError(
                    f"ERROR - Failed to dynamically load concrete class from path '{concrete_implementation_path}' for abstraction '{str(abstraction)}': {e}"
                ) from e
        elif not inspect.isabstract(abstraction):
            # If not explicitly registered, but it's a concrete class (not an interface/abstract),
            # assume we can try to instantiate it directly if its dependencies can be met.
            concrete_class = abstraction
        else:
            raise ValueError(f"ERROR - No concrete implementation registered for abstraction: {str(abstraction)}")

        if inspect.isabstract(concrete_class):
            raise ValueError(f"ERROR - Attempted to resolve an abstract class or interface without a concrete registration: {str(abstraction)}")

        constructor_params = inspect.signature(concrete_class.__init__).parameters
        dependencies = {}
        for name, param in constructor_params.items():
            if name == 'self':
                continue

            if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and param.annotation != inspect.Parameter.empty:
                # Loguru's logger is globally accessible, not injected here.
                # If a class asks for 'logging.Logger' (standard library logger), it's an error in Loguru mode.
                if param.annotation is logging.Logger:
                    raise ValueError(f"ERROR - Logger (logging.Logger) cannot be injected by DependencyContainer in Loguru mode. "
                                     f"Remove 'logger: logging.Logger' from '{concrete_class.__name__}' constructor and use 'from loguru import logger' directly.")

                try:
                    resolved_dependency = self.resolve(param.annotation)
                    dependencies[name] = resolved_dependency
                except ValueError as e:
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"ERROR - Cannot resolve required dependency '{name}' (type: {str(param.annotation)}) for '{concrete_class.__name__}': {e}")
                    else:
                        dependencies[name] = param.default
                        logger.warning(f"WARNING - Optional dependency '{name}' (type: {str(param.annotation)}) for '{concrete_class.__name__}' could not be resolved, using default value.")
            elif param.default != inspect.Parameter.empty:
                dependencies[name] = param.default
            else:
                raise ValueError(f"ERROR - Cannot resolve dependency '{name}' for '{concrete_class.__name__}': Missing type hint or default value.")

        logger.debug(f"DEBUG - Resolving {concrete_class.__name__} with dependencies: {list(dependencies.keys())}")
        return concrete_class(**dependencies)

