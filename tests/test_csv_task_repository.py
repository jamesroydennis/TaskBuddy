# taskbuddy_project/tests/test_csv_task_repository.py

import pytest
import uuid
import os
import shutil # For copying files
import tempfile # For creating temporary directories/files
from typing import List # This import is crucial for 'List' to be defined

# Ensure logging is set up for tests (configures Loguru)
import config.loguru_setup

# Import Loguru's logger directly
from loguru import logger

from data.csv_task_repository import CsvTaskRepository
from business.task import Task, TaskStatus

# Define the path to the read-only sample CSV data for source
SAMPLE_CSV_SOURCE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), # path to tests/
    '..', # go up to taskbuddy_project/
    'data', 'csv', 'sample_data.csv'
)

@pytest.fixture
def csv_repo():
    """
    Provides a CsvTaskRepository instance initialized with a temporary,
    writable copy of the sample CSV data.
    Loguru's global logger is used directly by the repository.
    """
    # 1. Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # 2. Define the path for the temporary CSV file within this directory
    temp_csv_file_path = os.path.join(temp_dir, 'test_tasks.csv')

    # 3. Copy the content from the read-only sample data to the temporary file
    try:
        shutil.copyfile(SAMPLE_CSV_SOURCE_PATH, temp_csv_file_path)
        logger.debug(f"Copied '{SAMPLE_CSV_SOURCE_PATH}' to temporary file '{temp_csv_file_path}'")
    except FileNotFoundError:
        pytest.fail(f"Source sample CSV file not found at: {SAMPLE_CSV_SOURCE_PATH}")
    except Exception as e:
        pytest.fail(f"Failed to create temporary CSV file: {e}")

    # 4. Instantiate CsvTaskRepository. It will use 'from loguru import logger' internally.
    repo = CsvTaskRepository(file_path=temp_csv_file_path)
    
    # 5. Yield the repository instance to the test function
    yield repo

    # 6. Teardown: Clean up the temporary directory and its contents after the test finishes
    try:
        shutil.rmtree(temp_dir)
        logger.debug(f"Cleaned up temporary directory: {temp_dir}")
    except OSError as e:
        logger.error(f"Failed to remove temporary directory {temp_dir}: {e}")


def test_get_all_tasks_returns_correct_number_of_tasks(csv_repo):
    """
    Test that get_all_tasks correctly reads all 20 tasks from the temporary CSV.
    """
    logger.info("Running test_get_all_tasks_returns_correct_number_of_tasks")
    tasks = csv_repo.get_all_tasks() # Calls ITaskRepository method
    assert len(tasks) == 20, f"Expected 20 tasks, but got {len(tasks)}"
    logger.info("Test passed: Found 20 tasks.")

def test_get_all_tasks_returns_task_objects(csv_repo):
    """
    Test that get_all_tasks returns a list where each element is an instance of Task.
    """
    logger.info("Running test_get_all_tasks_returns_task_objects")
    tasks = csv_repo.get_all_tasks() # Calls ITaskRepository method
    assert all(isinstance(task, Task) for task in tasks), "Not all returned items are Task objects."
    logger.info("Test passed: All returned items are Task objects.")


def test_get_all_tasks_parses_task_attributes_correctly(csv_repo):
    """
    Test that attributes (id, title, status) are correctly parsed for a specific task.
    """
    logger.info("Running test_get_all_tasks_parses_task_attributes_correctly")
    tasks = csv_repo.get_all_tasks() # Calls ITaskRepository method

    plumber_task = next((t for t in tasks if t.title == "Call plumber for leaky faucet"), None)
    assert plumber_task is not None, "Could not find 'Call plumber for leaky faucet' task."
    assert plumber_task.status == TaskStatus.PENDING, \
        f"Expected 'Call plumber' status to be PENDING, got {plumber_task.status}"

    budget_task = next((t for t in tasks if t.title == "Review Q3 budget report"), None)
    assert budget_task is not None, "Could not find 'Review Q3 budget report' task."
    assert budget_task.status == TaskStatus.COMPLETE, \
        f"Expected 'Budget report' status to be COMPLETE, got {budget_task.status}"

    presentation_task = next((t for t in tasks if t.title == "Prepare presentation for Monday"), None)
    assert presentation_task is not None, "Could not find 'Prepare presentation for Monday' task."
    assert presentation_task.status == TaskStatus.OVERDUE, \
        f"Expected 'Presentation' status to be OVERDUE, got {presentation_task.status}"

    known_id_str = "f0a3e8b1-1d2c-4e5f-8a9b-0c1d2e3f4a5b"
    known_id_task = next((t for t in tasks if str(t.id) == known_id_str), None)
    assert known_id_task is not None, f"Could not find task with ID {known_id_str}"
    assert known_id_task.title == "Call plumber for leaky faucet", \
        f"Expected title 'Call plumber' for ID {known_id_str}, got {known_id_task.title}"

    logger.info("Test passed: Task attributes parsed correctly.")

def test_get_all_tasks_handles_non_existent_file():
    """
    Test that get_all_tasks raises FileNotFoundError if the CSV file does not exist.
    """
    logger.info("Running test_get_all_tasks_handles_non_existent_file")
    non_existent_path = "path/to/non_existent/file.csv"
    repo = CsvTaskRepository(file_path=non_existent_path)
    with pytest.raises(FileNotFoundError):
        repo.get_all_tasks() # Calls ITaskRepository method
    logger.info("Test passed: FileNotFoundError correctly raised for non-existent file.")


def test_get_task_by_id_returns_correct_task(csv_repo):
    """
    Test that get_task_by_id returns the correct Task object for a known ID.
    """
    logger.info("Running test_get_task_by_id_returns_correct_task")
    known_id_str = "1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e"
    expected_title = "Schedule dentist appointment"
    expected_status = TaskStatus.PENDING

    known_id = uuid.UUID(known_id_str)
    retrieved_task = csv_repo.get_task_by_id(known_id)

    assert retrieved_task is not None, f"Task with ID {known_id_str} was not found."
    assert retrieved_task.id == known_id, "Retrieved task ID does not match expected ID."
    assert retrieved_task.title == expected_title, "Retrieved task title does not match."
    assert retrieved_task.status == expected_status, "Retrieved task status does not match."
    logger.info("Test passed: get_task_by_id returned correct task.")


def test_get_task_by_id_raises_value_error_for_non_existent_id(csv_repo):
    """
    Test that get_task_by_id raises a ValueError for a non-existent ID.
    """
    logger.info("Running test_get_task_by_id_raises_value_error_for_non_existent_id")
    non_existent_id = uuid.uuid4()

    with pytest.raises(ValueError) as excinfo:
        csv_repo.get_task_by_id(non_existent_id)

    assert f"task with ID '{non_existent_id}' not found." in str(excinfo.value), \
        "Expected 'task not found' error message for non-existent ID."
    logger.info("Test passed: get_task_by_id correctly raised ValueError for non-existent ID.")


def test_add_task_adds_new_task_to_repository(csv_repo):
    """
    Test that add_task successfully adds a new task and increases the task count.
    """
    logger.info("Running test_add_task_adds_new_task_to_repository")
    initial_tasks = csv_repo.get_all_tasks()
    initial_count = len(initial_tasks)

    new_task_title = "Buy birthday gift for Nova"
    new_task_to_add = Task(title=new_task_title, status=TaskStatus.PENDING)

    csv_repo.add_task(new_task_to_add)

    updated_tasks = csv_repo.get_all_tasks()
    updated_count = len(updated_tasks)

    assert updated_count == initial_count + 1, \
        f"Expected task count to increase by 1, but got {updated_count - initial_count}"
    assert new_task_to_add in updated_tasks, \
        f"New task '{new_task_title}' was not found in the repository after adding."

    retrieved_new_task = next((t for t in updated_tasks if t.id == new_task_to_add.id), None)
    assert retrieved_new_task is not None, "Added task could not be retrieved by its ID after adding."
    assert retrieved_new_task.title == new_task_title
    assert retrieved_new_task.status == TaskStatus.PENDING

    logger.info(f"Test passed: Task '{new_task_title}' successfully added.")


def test_update_task_modifies_existing_task(csv_repo):
    """
    Test that update_task successfully modifies an existing task's properties.
    """
    logger.info("Running test_update_task_modifies_existing_task")
    original_tasks = csv_repo.get_all_tasks()
    assert len(original_tasks) > 0, "Precondition: There must be at least one task to update."
    original_task = original_tasks[0]
    
    updated_title = "Updated: " + original_task.title
    updated_status = TaskStatus.COMPLETE if original_task.status == TaskStatus.PENDING else TaskStatus.PENDING
    
    modified_task = Task(
        title=updated_title,
        status=updated_status,
        task_id=original_task.id # Crucial: retain the original ID
    )

    csv_repo.update_task(modified_task)

    retrieved_task = csv_repo.get_task_by_id(modified_task.id)
    assert retrieved_task is not None, f"Updated task with ID {modified_task.id} not found after update attempt."
    assert retrieved_task.title == updated_title, "Task title was not updated correctly."
    assert retrieved_task.status == updated_status, "Task status was not updated correctly."
    
    final_tasks = csv_repo.get_all_tasks()
    assert len(final_tasks) == len(original_tasks), "Update operation should not change total task count."

    logger.info(f"Test passed: Task '{original_task.id}' successfully modified.")


def test_delete_task_removes_task_from_repository(csv_repo):
    """
    Test that delete_task successfully removes a task from the repository.
    """
    logger.info("Running test_delete_task_removes_task_from_repository")
    initial_tasks = csv_repo.get_all_tasks()
    initial_count = len(initial_tasks)
    
    assert initial_count > 0, "Precondition: There must be at least one task to delete."

    task_to_delete = initial_tasks[0]

    csv_repo.delete_task(task_to_delete.id)

    updated_tasks = csv_repo.get_all_tasks()
    updated_count = len(updated_tasks)

    assert updated_count == initial_count - 1, \
        f"Expected task count to decrease by 1, but got {updated_count - initial_count}"
    assert task_to_delete not in updated_tasks, \
        f"Task with ID '{task_to_delete.id}' was found in the repository after deletion."
        
    logger.info(f"Test passed: Task '{task_to_delete.id}' successfully removed.")