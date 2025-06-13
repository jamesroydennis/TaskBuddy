# taskbuddy_project/core/dependency_container.py

import inspect
import logging
import importlib # New import for dynamic loading

logger = logging.getLogger(__name__)

class DependencyContainer:
    """
    A simple Inversion of Control (IoC) container for managing dependencies.
    Allows for registering concrete implementations for interfaces/abstractions
    and resolving them.
    """
    def __init__(self):
        self._registrations = {} # Stores interface -> concrete_class mappings
        logger.debug("DependencyContainer initialized.")

    def register(self, abstraction: type, concrete_implementation_path: str):
        """
        Registers a concrete implementation for a given abstraction (interface or base class)
        by its full import path string.

        Args:
            abstraction (type): The interface or abstract class (e.g., ITaskRepository).
            concrete_implementation_path (str): The full import path string of the concrete class
                                                 (e.g., "data.csv_task_repository.CsvTaskRepository").
        Raises:
            ValueError: If the concrete implementation does not correctly implement
                        the abstraction, or if the path is invalid.
            ImportError: If the concrete implementation module cannot be found.
            AttributeError: If the class cannot be found within the module.
        """
        try:
            # Dynamically import the concrete implementation class
            module_path, class_name = concrete_implementation_path.rsplit('.', 1)
            concrete_module = importlib.import_module(module_path)
            concrete_implementation = getattr(concrete_module, class_name)
        except (ImportError, AttributeError, ValueError) as e:
            raise ValueError(
                f"Failed to load concrete implementation '{concrete_implementation_path}'. "
                f"Please check the path. Error: {e}"
            ) from e

        if not issubclass(concrete_implementation, abstraction):
            raise ValueError(f"Concrete implementation {concrete_implementation.__name__} "
                             f"does not implement abstraction {abstraction.__name__}.")

        self._registrations[abstraction] = concrete_implementation
        logger.debug(f"Registered {concrete_implementation.__name__} for {abstraction.__name__}")

    def resolve(self, abstraction: type):
        """
        Resolves and returns an instance of the concrete implementation
        registered for the given abstraction. Handles nested dependencies recursively.

        Args:
            abstraction (type): The interface or concrete class to resolve.
                                If a concrete class is passed and not registered,
                                it will attempt to instantiate it directly by resolving its dependencies.

        Returns:
            object: An instance of the resolved concrete class.

        Raises:
            ValueError: If no implementation is registered for the abstraction.
            Exception: For errors during instantiation of dependencies.
        """
        # If the abstraction itself is registered, get its concrete implementation
        concrete_class = self._registrations.get(abstraction, abstraction)

        # If it's still an abstraction at this point and not a registered concrete class,
        # it means it was never explicitly registered to begin with.
        if inspect.isabstract(concrete_class):
            raise ValueError(f"No concrete implementation registered for abstraction: {abstraction.__name__}")

        # Get the constructor signature
        constructor_params = inspect.signature(concrete_class.__init__).parameters

        dependencies = {}
        for name, param in constructor_params.items():
            if name == 'self':
                continue # Skip 'self' parameter

            # If parameter has a type annotation, try to resolve it
            if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and param.annotation != inspect.Parameter.empty:
                try:
                    # Recursively resolve dependencies
                    dependencies[name] = self.resolve(param.annotation)
                except ValueError as e:
                    # If a dependency cannot be resolved and it's not optional, raise an error
                    if param.default == inspect.Parameter.empty: # Not an optional parameter
                        raise ValueError(f"Cannot resolve dependency '{name}' for '{concrete_class.__name__}': {e}")
                    else:
                        # If optional, use its default value (not injected)
                        dependencies[name] = param.default
                        logger.warning(f"Optional dependency '{name}' for '{concrete_class.__name__}' could not be resolved, using default value.")
            elif param.default != inspect.Parameter.empty:
                # If a parameter has a default value and no type hint, use the default
                dependencies[name] = param.default
            else:
                # If a parameter has no type hint and no default, we cannot resolve it
                raise ValueError(f"Cannot resolve dependency '{name}' for '{concrete_class.__name__}': Missing type hint or default value.")

        logger.debug(f"Resolving {concrete_class.__name__} with dependencies: {list(dependencies.keys())}")
        return concrete_class(**dependencies)

