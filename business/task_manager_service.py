# taskbuddy_project/business/task_manager_service.py

import logging
from typing import List, Optional
import uuid # For get_task_by_id

from business.interfaces.ITaskRepository import ITaskRepository
from business.task import Task, TaskStatus

logger = logging.getLogger(__name__)

class TaskManagerService:
    """
    Manages business logic related to tasks.
    It depends on an ITaskRepository abstraction, demonstrating Dependency Inversion.
    """
    def __init__(self, task_repository: ITaskRepository):
        """
        Initializes the TaskManagerService with a concrete implementation
        of ITaskRepository.

        Args:
            task_repository (ITaskRepository): The repository to use for task data operations.
        """
        if not isinstance(task_repository, ITaskRepository):
            raise TypeError("task_repository must be an instance of ITaskRepository.")
        self._task_repository = task_repository
        logger.debug(f"TaskManagerService initialized with repository: {type(task_repository).__name__}")

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieves all tasks using the injected repository.
        Returns:
            List[Task]: A list of all tasks.
        """
        logger.info("Retrieving all tasks from repository.")
        try:
            return self._task_repository.get_all_tasks()
        except Exception as e:
            logger.error(f"Error retrieving all tasks: {e}", exc_info=True)
            return [] # Return empty list or re-raise based on error handling policy

    def get_task_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        """
        Retrieves a single task by its ID using the injected repository.
        Returns:
            Optional[Task]: The Task object if found, otherwise None.
        """
        logger.info(f"Retrieving task with ID: {task_id}")
        try:
            return self._task_repository.get_task_by_id(task_id)
        except ValueError as e:
            logger.warning(f"Task with ID {task_id} not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving task by ID {task_id}: {e}", exc_info=True)
            return None

    def add_new_task(self, title: str) -> Task:
        """
        Creates and adds a new task to the repository.
        Args:
            title (str): The title for the new task.
        Returns:
            Task: The newly created and added Task object.
        """
        logger.info(f"Attempting to add new task: '{title}'")
        new_task = Task(title=title, status=TaskStatus.PENDING)
        try:
            self._task_repository.add_task(new_task)
            logger.info(f"Successfully added task: {new_task}")
            return new_task
        except Exception as e:
            logger.error(f"Error adding new task '{title}': {e}", exc_info=True)
            raise # Re-raise to signal failure to caller

    def mark_task_complete(self, task_id: uuid.UUID) -> bool:
        """
        Marks a task as complete.
        Returns:
            bool: True if task was found and marked complete, False otherwise.
        """
        logger.info(f"Attempting to mark task {task_id} as complete.")
        task = self.get_task_by_id(task_id)
        if task:
            task.mark_complete()
            try:
                self._task_repository.update_task(task)
                logger.info(f"Task {task_id} marked as complete.")
                return True
            except Exception as e:
                logger.error(f"Error updating task {task_id} to complete: {e}", exc_info=True)
                return False
        logger.warning(f"Task {task_id} not found for marking complete.")
        return False

    def delete_task_by_id(self, task_id: uuid.UUID) -> bool:
        """
        Deletes a task by its ID.
        Returns:
            bool: True if task was found and deleted, False otherwise.
        """
        logger.info(f"Attempting to delete task with ID: {task_id}")
        try:
            self._task_repository.delete_task(task_id)
            logger.info(f"Task {task_id} deleted successfully.")
            return True
        except ValueError as e:
            logger.warning(f"Task {task_id} not found for deletion: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
            return False
