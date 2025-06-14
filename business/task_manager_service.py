# taskbuddy_project/business/task_manager_service.py

from typing import List, Optional
import uuid

from business.interfaces.ITaskRepository import ITaskRepository
from business.task import Task, TaskStatus

from loguru import logger

class TaskManagerService:
    """
    Manages business logic related to tasks.
    It depends on an ITaskRepository abstraction and uses the globally configured Loguru logger directly.
    """
    def __init__(self, task_repository: ITaskRepository):
        if not isinstance(task_repository, ITaskRepository):
            # Removed manual "CRITICAL - " from message
            logger.critical(f"Provided task_repository is not an instance of ITaskRepository: {type(task_repository).__name__}")
            raise TypeError("task_repository must be an instance of ITaskRepository.")
        self._task_repository = task_repository
        # Removed manual "DEBUG - " from message
        logger.debug(f"TaskManagerService initialized with repository: {type(task_repository).__name__}")

    def get_all_tasks(self) -> List[Task]:
        # Removed manual "INFO - " from message
        logger.info("Retrieving all tasks from repository.")
        try:
            return self._task_repository.get_all_tasks()
        except Exception as e:
            # Removed manual "ERROR - " from message
            logger.error(f"Error retrieving all tasks: {e}", exc_info=True)
            return []

    def get_task_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        # Removed manual "INFO - " from message
        logger.info(f"Retrieving task with ID: {task_id}")
        try:
            return self._task_repository.get_task_by_id(task_id)
        except ValueError as e:
            # Removed manual "WARNING - " from message
            logger.warning(f"Task with ID {task_id} not found: {e}")
            return None
        except Exception as e:
            # Removed manual "ERROR - " from message
            logger.error(f"Error retrieving task by ID {task_id}: {e}", exc_info=True)
            return None

    def add_new_task(self, title: str) -> Task:
        # Removed manual "INFO - " from message
        logger.info(f"Attempting to add new task: '{title}'")
        new_task = Task(title=title, status=TaskStatus.PENDING)
        try:
            self._task_repository.add_task(new_task)
            # Removed manual "INFO - " from message
            logger.info(f"Successfully added task: {new_task}")
            return new_task
        except Exception as e:
            # Removed manual "ERROR - " from message
            logger.error(f"Error adding new task '{title}': {e}", exc_info=True)
            raise

    def mark_task_complete(self, task_id: uuid.UUID) -> bool:
        # Removed manual "INFO - " from message
        logger.info(f"Attempting to mark task {task_id} as complete.")
        task = self.get_task_by_id(task_id)
        if task:
            task.mark_complete()
            try:
                self._task_repository.update_task(task)
                # Removed manual "INFO - " from message
                logger.info(f"Task {task_id} marked as complete.")
                return True
            except Exception as e:
                # Removed manual "ERROR - " from message
                logger.error(f"Error updating task {task_id} to complete: {e}", exc_info=True)
                return False
        # Removed manual "WARNING - " from message
        logger.warning(f"Task {task_id} not found for marking complete.")
        return False

    def delete_task_by_id(self, task_id: uuid.UUID) -> bool:
        # Removed manual "INFO - " from message
        logger.info(f"Attempting to delete task with ID: {task_id}")
        try:
            self._task_repository.delete_task(task_id)
            # Removed manual "INFO - " from message
            logger.info(f"Task {task_id} deleted successfully.")
            return True
        except ValueError as e:
            # Removed manual "WARNING - " from message
            logger.warning(f"Task {task_id} not found for deletion: {e}")
            return False
        except Exception as e:
            # Removed manual "ERROR - " from message
            logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
            return False
