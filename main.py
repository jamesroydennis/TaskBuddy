# taskbuddy_project/main.py

import argparse
import sys
import os

from loguru import logger

# Ensure Loguru's global logger is configured at startup
import config.loguru_setup

from config.config import DEBUG_MODE

from core.dependency_container import DependencyContainer

# Import the ITaskRepository interface (our specific task contract)
from business.interfaces.ITaskRepository import ITaskRepository

from task import Task
from task_manager_service import TaskManagerService


def configure_dependencies(container: DependencyContainer):
    """
    Registers all application dependencies with the container.
    This is the central wiring logic.
    """
    # Removed manual "INFO - " from message
    logger.info("Configuring application dependencies...")

    container.register(ITaskRepository, "data.csv_task_repository.CsvTaskRepository")

    # Removed manual "INFO - " from message
    logger.info("Dependencies configured.")


def run_application(current_debug_mode: str):
    """
    Main function to run the TaskBuddy application logic.
    It resolves the main service from the container.
    """
    # Removed manual "INFO - " from message
    logger.info("TaskBuddy application starting...")
    
    # Demonstrate custom console/file logging methods (these methods handle adding levels internally)
    logger.file(f"[FILE_ONLY] Application starting in {current_debug_mode} mode.")
    logger.console(f"[CONSOLE_ONLY] Application starting in {current_debug_mode} mode.")

    # --- Dependency Injection: Initialize container and resolve main service ---
    container = DependencyContainer()
    configure_dependencies(container)

    try:
        task_service = container.resolve(TaskManagerService)
        # Removed manual "INFO - " from message
        logger.info(f"Main service '{TaskManagerService.__name__}' resolved with its dependencies.")

    except Exception as e:
        # Removed manual "CRITICAL - " from message
        logger.critical(f"A critical error occurred during service resolution: {e}", exc_info=True)
        print(f"\nFATAL ERROR: Could not initialize application services. Error: {e}")
        sys.exit(1)

    # --- Application Logic Starts Here ---
    try:
        tasks = task_service.get_all_tasks()
        # Removed manual "INFO - " from message
        logger.info(f"Successfully loaded {len(tasks)} tasks.")
        print("\nCurrent Tasks:")
        for task in tasks:
            print(f"  - [{task.status.value.upper()}] {task.title} (ID: {task.id})")

    except Exception as e:
        # Removed manual "ERROR - " from message
        logger.error(f"An error occurred during application run: {e}", exc_info=True)

    # Removed manual "INFO - " from message
    logger.info("TaskBuddy application finished.")
    logger.file(" [FILE_ONLY] Application session ended.")


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

    effective_debug_mode = 'test' if args.test else DEBUG_MODE

    config.loguru_setup.setup_logging() 
    
    main_logger = logger # This is Loguru's global logger 

    if args.test:
        # Removed manual "INFO - " from message
        main_logger.info("--- Running Tests for TaskBuddy ---")

        try:
            import pytest
        except ImportError:
            # Removed manual "ERROR - " from message
            main_logger.error("pytest is not installed. Please install it with 'pip install pytest'.")
            sys.exit(1)

        current_working_dir = os.getcwd()
        project_root_dir = os.path.dirname(os.path.abspath(__file__))

        os.chdir(project_root_dir)

        test_path = os.path.join(project_root_dir, 'tests')
        
        exit_code = pytest.main([test_path, "--capture=sys"])

        os.chdir(current_working_dir)

        sys.exit(exit_code)

    else:
        print("\n--- Starting TaskBuddy Application ---")
        run_application(effective_debug_mode)


if __name__ == "__main__":
    main()

