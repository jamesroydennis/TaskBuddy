# taskbuddy_project/tests/test_csv_task_repository.py

import pytest
import uuid
import os
import logging

# Ensure logging is set up for tests - now from config folder
import config.logging_setup # This will run setup_logging()

from data.csv_task_repository import CsvTaskRepository
from business.task import Task, TaskStatus

logger = logging.getLogger(__name__)

# Define the path to the sample CSV data specifically for tests
# It's good practice to make test paths explicit or use fixtures
# Here we calculate it relative to the test file itself for robustness
TEST_CSV_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), # path to tests/
    '..', # go up to taskbuddy_project/
    'data', 'csv', 'sample_data.csv'
)

# Use a fixture to provide a CsvTaskRepository instance for tests
@pytest.fixture
def csv_repo():
    """Provides a CsvTaskRepository instance initialized with the test CSV."""
    # Ensure the test CSV file actually exists before running tests
    if not os.path.exists(TEST_CSV_FILE_PATH):
        pytest.fail(f"Test CSV file not found at: {TEST_CSV_FILE_PATH}")
    return CsvTaskRepository(file_path=TEST_CSV_FILE_PATH)

def test_get_all_tasks_returns_correct_number_of_tasks(csv_repo):
    """
    Test that get_all_tasks correctly reads all 20 tasks from the sample CSV.
    """
    logger.info("Running test_get_all_tasks_returns_correct_number_of_tasks")
    tasks = csv_repo.get_all_tasks()
    assert len(tasks) == 20, f"Expected 20 tasks, but got {len(tasks)}"
    logger.info(f"Test passed: Found {len(tasks)} tasks.")

def test_get_all_tasks_returns_task_objects(csv_repo):
    """
    Test that get_all_tasks returns a list where each element is an instance of Task.
    """
    logger.info("Running test_get_all_tasks_returns_task_objects")
    tasks = csv_repo.get_all_tasks()
    assert all(isinstance(task, Task) for task in tasks), "Not all returned items are Task objects."
    logger.info("Test passed: All returned items are Task objects.")


def test_get_all_tasks_parses_task_attributes_correctly(csv_repo):
    """
    Test that attributes (id, title, status) are correctly parsed for a specific task.
    We'll check a few known tasks from the sample_data.csv.
    """
    logger.info("Running test_get_all_tasks_parses_task_attributes_correctly")
    tasks = csv_repo.get_all_tasks()

    # Find a specific task (e.g., "Call plumber for leaky faucet")
    plumber_task = next((t for t in tasks if t.title == "Call plumber for leaky faucet"), None)
    assert plumber_task is not None, "Could not find 'Call plumber for leaky faucet' task."
    assert plumber_task.status == TaskStatus.PENDING, \
        f"Expected 'Call plumber' status to be PENDING, got {plumber_task.status}"

    # Find another specific task (e.g., "Review Q3 budget report")
    budget_task = next((t for t in tasks if t.title == "Review Q3 budget report"), None)
    assert budget_task is not None, "Could not find 'Review Q3 budget report' task."
    assert budget_task.status == TaskStatus.COMPLETE, \
        f"Expected 'Budget report' status to be COMPLETE, got {budget_task.status}"

    # Find an overdue task (e.g., "Prepare presentation for Monday")
    presentation_task = next((t for t in tasks if t.title == "Prepare presentation for Monday"), None)
    assert presentation_task is not None, "Could not find 'Prepare presentation for Monday' task."
    assert presentation_task.status == TaskStatus.OVERDUE, \
        f"Expected 'Presentation' status to be OVERDUE, got {presentation_task.status}"

    # Check a UUID specifically
    # Example ID from sample_data.csv: f0a3e8b1-1d2c-4e5f-8a9b-0c1d2e3f4a5b
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
    # Create a CsvTaskRepository instance, passing a path that definitely does not exist
    repo = CsvTaskRepository(file_path=non_existent_path)
    with pytest.raises(FileNotFoundError):
        # We expect a FileNotFoundError when get_all_tasks tries to open this path
        repo.get_all_tasks()
    logger.info("Test passed: FileNotFoundError correctly raised for non-existent file.")

def test_add_task_raises_not_implemented_error(csv_repo):
    """
    Test that add_task method raises NotImplementedError as expected,
    since the current CsvTaskRepository is designed for read-only sample data.
    """
    logger.info("Running test_add_task_raises_not_implemented_error")
    # Create a dummy task to attempt adding
    new_task = Task(title="Test Task for Add", status=TaskStatus.PENDING)

    # Assert that calling add_task raises NotImplementedError
    with pytest.raises(NotImplementedError) as excinfo:
        csv_repo.add_task(new_task)

    # Optionally, check the error message
    assert "add_task is not implemented" in str(excinfo.value), \
        "Expected 'add_task is not implemented' in the error message."
    logger.info("Test passed: add_task correctly raised NotImplementedError.")


def test_get_task_by_id_returns_correct_task(csv_repo):
    """
    Test that get_task_by_id returns the correct Task object for a known ID.
    """
    logger.info("Running test_get_task_by_id_returns_correct_task")
    # Pick a known ID and its expected details from sample_data.csv
    known_id_str = "1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e" # Schedule dentist appointment
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
    non_existent_id = uuid.uuid4() # Generate a truly random, non-existent UUID

    with pytest.raises(ValueError) as excinfo:
        csv_repo.get_task_by_id(non_existent_id)

    assert f"Task with ID '{non_existent_id}' not found." in str(excinfo.value), \
        "Expected 'Task not found' error message for non-existent ID."
    logger.info("Test passed: get_task_by_id correctly raised ValueError for non-existent ID.")

