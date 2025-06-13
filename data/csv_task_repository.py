# taskbuddy_project/data/csv_task_repository.py

import csv
import uuid
import os
import logging
from typing import List, Optional # Import Optional for type hinting

from business.interfaces.ITaskRepository import ITaskRepository
from business.task import Task, TaskStatus # Import Task and TaskStatus from our model
from config.config import DEBUG_MODE # Import from new config location

logger = logging.getLogger(__name__)

class CsvTaskRepository(ITaskRepository):
    """
    Concrete implementation of ITaskRepository for CSV file storage.
    Handles reading and writing Task objects to a CSV file.
    """
    def __init__(self, file_path: str = None):
        """
        Initializes the CsvTaskRepository.

        Args:
            file_path (str, optional): The path to the CSV file.
                                       Defaults to 'data/csv/sample_data.csv'
                                       relative to the project root.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir)) # Go up two levels from data/ to taskbuddy_project/

        if file_path:
            self.file_path = file_path
        else:
            self.file_path = os.path.join(project_root, 'data', 'csv', 'sample_data.csv')

        logger.debug(f"DEBUG - CsvTaskRepository initialized. Expected file_path: {self.file_path}")


    def get_all_tasks(self) -> List[Task]:
        """
        Retrieves all tasks from the CSV file.
        Reads the CSV row by row, parses the data, and constructs Task objects.
        """
        tasks: List[Task] = []
        try:
            if not os.path.exists(self.file_path):
                # Changed to WARNING as it's often an expected scenario in tests
                # or a recoverable state for the application logic.
                logger.warning(f"WARNING - CSV file not found at: {self.file_path}")
                raise FileNotFoundError(f"CSV file not found at: {self.file_path}")

            with open(self.file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                logger.debug(f"DEBUG - Successfully opened CSV file: {self.file_path}")

                first_line_content = csvfile.readline().strip()
                if not first_line_content:
                    logger.warning(f"WARNING - CSV file '{self.file_path}' is empty or contains only whitespace.")
                    return [] # Return empty list if file is empty

                csvfile.seek(0) # Rewind to the beginning for DictReader

                reader = csv.DictReader(csvfile)

                if not reader.fieldnames:
                    logger.error(f"ERROR - CSV file '{self.file_path}' has no header row or is malformed. Content: '{first_line_content}'")
                    return [] # Return empty if no valid header

                logger.debug(f"DEBUG - CSV headers found: {reader.fieldnames}")

                expected_headers = {'id', 'title', 'status'}
                if not expected_headers.issubset(set(reader.fieldnames)):
                    logger.error(f"ERROR - Missing expected headers in CSV. Expected: {expected_headers}, Found: {reader.fieldnames}")
                    return [] # Or raise a specific error

                for row_num, row in enumerate(reader):
                    try:
                        if not all(field in row and row[field] is not None for field in ['id', 'title', 'status']):
                             logger.warning(f"WARNING - Skipping row {row_num + 2} (including header) due to missing or None values for required fields: {row}")
                             continue

                        task_id_str = row['id'].strip()
                        title_str = row['title'].strip()
                        status_raw_str = row['status'].strip()

                        if not task_id_str or not title_str or not status_raw_str:
                             logger.warning(f"WARNING - Skipping row {row_num + 2} due to empty required fields after strip: {row}")
                             continue

                        task_id = uuid.UUID(task_id_str)
                        status = TaskStatus[status_raw_str.upper()]

                        task = Task(title=title_str, status=status, task_id=task_id)
                        tasks.append(task)

                    except ValueError as e:
                        logger.error(f"ERROR - Data conversion error in row {row_num + 2} (ID/Status): {e}. Row: {row}", exc_info=False)
                    except KeyError as e:
                        logger.error(f"ERROR - Missing expected column in row {row_num + 2}: {e}. Row: {row}", exc_info=False)
                    except Exception as e:
                        logger.error(f"ERROR - Unexpected error processing row {row_num + 2}: {e}. Row: {row}", exc_info=False)

        except FileNotFoundError:
            # This is the expected place for FileNotFoundError to be raised
            logger.warning(f"WARNING - CSV file not found when attempting to read: {self.file_path}") # Changed to WARNING
            raise # Re-raise to let the test (or calling code) handle it
        except Exception as e:
            logger.critical(f"CRITICAL - An unhandled error occurred while processing CSV file '{self.file_path}': {e}", exc_info=True)
            raise

        logger.info(f"INFO - Successfully loaded {len(tasks)} tasks from {self.file_path}")
        return tasks

    def get_task_by_id(self, task_id: uuid.UUID) -> Task:
        """
        Retrieves a single task by its ID from the CSV file.
        Args:
            task_id (uuid.UUID): The UUID of the task to retrieve.
        Returns:
            Task: The Task object if found.
        Raises:
            ValueError: If no task with the given ID is found.
        """
        logger.debug(f"DEBUG - Attempting to retrieve task with ID: {task_id}")
        all_tasks = self.get_all_tasks() # Re-use existing get_all_tasks
        for task in all_tasks:
            if task.id == task_id:
                logger.info(f"INFO - Found task with ID {task_id}: {task.title}")
                return task
        logger.warning(f"WARNING - Task with ID '{task_id}' not found in {self.file_path}.")
        raise ValueError(f"Task with ID '{task_id}' not found.")


    def add_task(self, task: Task):
        """Adds a new task. (Not implemented for read-only sample_data.csv)"""
        raise NotImplementedError("add_task is not implemented for CsvTaskRepository yet.")

    def update_task(self, task: Task):
        """Updates an existing task. (Not implemented for read-only sample_data.csv)"""
        raise NotImplementedError("update_task is not implemented for CsvTaskRepository yet.")

    def delete_task(self, task_id: uuid.UUID):
        """Deletes a task. (Not implemented for read-only sample_data.csv)"""
        raise NotImplementedError("delete_task is not implemented for CsvTaskRepository yet.")

