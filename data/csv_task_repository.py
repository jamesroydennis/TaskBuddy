# taskbuddy_project/data/csv_task_repository.py

import uuid
import os
from typing import Dict, Any, List # ADDED List to imports

# Import the BaseCsvRepository
from data.base_csv_repository import BaseCsvRepository

# Import the ITaskRepository interface
from business.interfaces.ITaskRepository import ITaskRepository

# Import Task model
from task import Task, TaskStatus

# Import Loguru's logger directly
from loguru import logger

class CsvTaskRepository(BaseCsvRepository[Task], ITaskRepository):
    """
    Concrete CSV repository for Task entities.
    Inherits generic CSV handling and CRUD implementation from BaseCsvRepository.
    Implements ITaskRepository by adapting its task-specific method names
    to the generic CRUD methods provided by BaseCsvRepository.
    """
    def __init__(self, file_path: str = None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        if file_path:
            resolved_file_path = file_path
        else:
            resolved_file_path = os.path.join(project_root, 'data', 'csv', 'sample_data.csv')
            
        super().__init__(file_path=resolved_file_path, entity_name="task")

        self._expected_headers = ['id', 'title', 'status']
        logger.debug(f"CsvTaskRepository initialized for tasks. File: {self.file_path}")


    def _to_dict(self, task: Task) -> Dict[str, Any]:
        """
        Converts a Task object into a dictionary suitable for writing to a CSV row.
        Implements the abstract method from BaseCsvRepository.
        """
        return {
            'id': str(task.id),
            'title': task.title,
            'status': task.status.value
        }

    def _from_dict(self, row: Dict[str, str]) -> Task:
        """
        Converts a dictionary (CSV row) into a Task object.
        Implements the abstract method from BaseCsvRepository.
        """
        try:
            task_id = uuid.UUID(row['id'].strip())
            title = row['title'].strip()
            status = TaskStatus[row['status'].strip().upper()]
            return Task(title=title, status=status, task_id=task_id)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to convert CSV row to Task object: {e}. Row: {row}", exc_info=False)
            raise ValueError(f"Invalid task data in CSV row: {row}. Error: {e}")

    # --- Implement ITaskRepository methods by delegating to BaseCsvRepository's generic methods ---

    def add_task(self, task: Task):
        """Adds a new task to the repository."""
        self.add(task)

    def get_all_tasks(self) -> List[Task]:
        """Retrieves all tasks from the repository."""
        return self.get_all()

    def get_task_by_id(self, task_id: uuid.UUID) -> Task:
        """Retrieves a single task by its ID."""
        return self.get_by_id(task_id)

    def update_task(self, task: Task):
        """Updates an existing task in the repository."""
        self.update(task)

    def delete_task(self, task_id: uuid.UUID):
        """Deletes a task from the repository."""
        self.delete(task_id)

