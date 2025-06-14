# taskbuddy_project/business/interfaces/ICrudRepository.py

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
import uuid
# logging import is no longer needed here as logger is not part of interface contract

# Define a TypeVar for the entity type to make the interface generic
T = TypeVar('T')

class ICrudRepository(ABC, Generic[T]):
    """
    Abstract Base Class for a generic CRUD (Create, Read, Update, Delete) repository.
    Defines the fundamental operations for managing entities in a persistence store.
    Concrete implementations will use a globally configured logger (e.g., Loguru).
    """
    # NO __init__ here, so it does not mandate a logger in the constructor.
    # This aligns with the Loguru paradigm where logger is globally accessed by implementations.

    @abstractmethod
    def add(self, entity: T):
        """
        Adds a new entity to the repository.
        Args:
            entity (T): The entity object to add.
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: uuid.UUID) -> T:
        """
        Retrieves a single entity by its ID.
        Args:
            entity_id (uuid.UUID): The UUID of the entity to retrieve.
        Returns:
            T: The entity object if found.
        Raises:
            ValueError: If no entity with the given ID is found.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Retrieves all entities from the repository.
        Returns:
            List[T]: A list of all entity objects.
        """
        pass

    @abstractmethod
    def update(self, entity: T):
        """
        Updates an existing entity in the repository.
        The entity is identified by its ID.
        Args:
            entity (T): The entity object with updated information.
        Raises:
            ValueError: If no entity with the given ID is found for update.
        """
        pass

    @abstractmethod
    def delete(self, entity_id: uuid.UUID):
        """
        Deletes an entity from the repository by its ID.
        Args:
            entity_id (uuid.UUID): The UUID of the entity to delete.
        Raises:
            ValueError: If no entity with the given ID is found for deletion.
        """
        pass

