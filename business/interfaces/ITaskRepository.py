# taskbuddy_project/business/interfaces/ITaskRepository.py

from abc import abstractmethod
from typing import List
import uuid

# Import the generic ICrudRepository and Task model
from business.interfaces.ICrudRepository import ICrudRepository
from task import Task

# ITaskRepository now inherits from ICrudRepository, specializing it for Task entities
class ITaskRepository(ICrudRepository[Task]):
    """
    Abstract Base Class for Task Repositories.
    Defines the contract for any class that provides CRUD operations for Task objects.
    It specializes the generic ICrudRepository for Task entities,
    requiring task-specific method names.
    """

    # These abstract methods mandate the task-specific naming for CRUD operations.
    # They implicitly override the generic methods from ICrudRepository.

    @abstractmethod
    def add_task(self, task: Task):
        """
        Adds a new task to the repository.
        Args:
            task (Task): The Task object to add.
        """
        pass

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieves all tasks from the repository.
        Returns:
            List[Task]: A list of Task objects.
        """
        pass

    @abstractmethod
    def get_task_by_id(self, task_id: uuid.UUID) -> Task:
        """
        Retrieves a single task by its ID.
        Args:
            task_id (uuid.UUID): The UUID of the task to retrieve.
        Returns:
            Task: The Task object if found.
        Raises:
            ValueError: If no task with the given ID is found.
        """
        pass

    @abstractmethod
    def update_task(self, task: Task):
        """
        Updates an existing task in the repository.
        The task is identified by its ID.
        Args:
            task (Task): The Task object with updated information.
        Raises:
            ValueError: If no task with the given ID is found for update.
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: uuid.UUID):
        """
        Deletes a task from the repository by its ID.
        Args:
            task_id (uuid.UUID): The UUID of the task to delete.
        Raises:
            ValueError: If no task with the given ID is found for deletion.
        """
        pass

