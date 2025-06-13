# taskbuddy_project/main.py

import argparse
import logging
import sys
import os

# Import logging_setup to configure logging for the application
from config.logging_setup import setup_logging
from config.config import DEBUG_MODE as DEFAULT_DEBUG_MODE # Import debug mode from di_config

# Import our custom Dependency Container
from core.dependency_container import DependencyContainer

# Import interfaces and business services (these are still direct imports
# as they define the contract and top-level services main directly interacts with)
from business.interfaces.ITaskRepository import ITaskRepository
from business.task_manager_service import TaskManagerService


def configure_dependencies(container: DependencyContainer):
    """
    Registers all application dependencies with the container using string paths.
    This is the central wiring logic.
    """
    logger = logging.getLogger(__name__) # Get logger instance
    logger.info("Configuring application dependencies...")

    # Register ITaskRepository to use CsvTaskRepository as its concrete implementation
    # Now passing the string path to the concrete class
    container.register(ITaskRepository, "data.csv_task_repository.CsvTaskRepository")
    # To switch to a database repository (if DbTaskRepository exists):
    # container.register(ITaskRepository, "data.db_task_repository.DbTaskRepository")

    logger.info("Dependencies configured.")


def run_application(current_debug_mode: str):
    """
    Main function to run the TaskBuddy application logic.
    It resolves the main service from the container.
    """
    logger = logging.getLogger(__name__) # Get logger after setup_logging is called

    logger.info("TaskBuddy application starting...")
    logger.info(f"Application running in {current_debug_mode} mode.")

    # --- Dependency Injection: Initialize container and resolve main service ---
    container = DependencyContainer()
    configure_dependencies(container) # Wire up all the dependencies

    try:
        # Ask the container for the TaskManagerService.
        # The container will automatically resolve TaskManagerService's
        # dependencies (like ITaskRepository).
        task_service = container.resolve(TaskManagerService)
        logger.info(f"Main service '{TaskManagerService.__name__}' resolved with its dependencies.")

    except Exception as e:
        logger.critical(f"A critical error occurred during service resolution: {e}", exc_info=True)
        print(f"\nFATAL ERROR: Could not initialize application services. Error: {e}")
        sys.exit(1)

    # --- Application Logic Starts Here ---
    # Now you can use task_service to perform operations
    # Example:
    try:
        tasks = task_service.get_all_tasks()
        logger.info(f"Successfully loaded {len(tasks)} tasks.")
        for task in tasks:
            logger.info(f"  - {task}")

        # Example: Add a new task (will raise NotImplementedError for CsvTaskRepository)
        # try:
        #     new_task = task_service.add_new_task("Learn Dependency Injection")
        #     logger.info(f"Attempted to add new task: {new_task}")
        # except NotImplementedError as e:
        #     logger.warning(f"Cannot add new task with current repository: {e}")
        # except Exception as e:
        #     logger.error(f"Error adding task: {e}")

    except Exception as e:
        logger.error(f"An error occurred during application run: {e}", exc_info=True)

    logger.info("TaskBuddy application finished.")


def main():
    """
    Parses command-line arguments and orchestrates application or test execution.
    """
    parser = argparse.ArgumentParser(description="TaskBuddy - Voice Memo Task Manager")
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run all tests and set debug mode to "test".'
    )
    args = parser.parse_args()

    # Determine the debug mode based on args and di_config
    effective_debug_mode = 'test' if args.test else DEFAULT_DEBUG_MODE

    # Configure logging first thing
    setup_logging(debug_mode_override=effective_debug_mode)
    logger = logging.getLogger(__name__) # Get a logger instance after logging is set up


    if args.test:
        logger.info("--- Running Tests for TaskBuddy ---")

        # Dynamically import and run pytest
        try:
            import pytest
        except ImportError:
            logger.error("pytest is not installed. Please install it with 'pip install pytest'.")
            sys.exit(1)

        # Pytest needs to be run from the project root for module imports to work correctly
        current_working_dir = os.getcwd()
        project_root_dir = os.path.dirname(os.path.abspath(__file__))

        os.chdir(project_root_dir) # Change directory to the project root temporarily

        # Run pytest.main(). Pass specific arguments if needed, e.g., ['-v'] for verbose
        # We also want to pass the path to the tests directory to pytest
        test_path = os.path.join(project_root_dir, 'tests')
        exit_code = pytest.main([test_path])

        os.chdir(current_working_dir) # Change back to original directory

        sys.exit(exit_code) # Exit with pytest's exit code

    else:
        # Default application run
        print("\n--- Starting TaskBuddy Application ---")
        run_application(effective_debug_mode)


if __name__ == "__main__":
    main()

