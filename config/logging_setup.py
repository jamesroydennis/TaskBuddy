# taskbuddy_project/config/logging_setup.py

import logging
import os
from config.config import DEBUG_MODE as DEFAULT_DEBUG_MODE

def setup_logging(debug_mode_override: str = None):
    """
    Configures the logging for the TaskBuddy application.
    Ensures that logging is set up only once and handles pytest's output capture.

    Args:
        debug_mode_override (str, optional): If provided, this value will
                                             override the DEBUG_MODE from config.py
                                             for this logging session.
    """
    # Determine the effective debug mode
    effective_debug_mode = debug_mode_override if debug_mode_override else DEFAULT_DEBUG_MODE

    # Get the root logger
    root_logger = logging.getLogger()

    # Clear existing handlers to prevent multiple handler additions,
    # which often causes issues with test runners like pytest.
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
        root_logger.handlers.clear()

    # Always ensure a basic configuration is set for the root logger.
    # Set it to INFO for 'test' and 'prod' modes, DEBUG for 'dev' mode.
    # This allows test INFO messages to show.
    if effective_debug_mode == 'dev':
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO) # Keep INFO for tests (to see test messages) and prod

    # Add a StreamHandler to ensure messages go to console.
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        handler = logging.StreamHandler()
        # Updated formatter to include file path and line number
        formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(pathname)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # --- Selective Logger Level Adjustment for 'test' mode ---
    if effective_debug_mode == 'test':
        # Identify the specific loggers you want to silence warnings from during tests.
        # Set their level to ERROR or higher to suppress WARNING and INFO messages.
        logging.getLogger('data.csv_task_repository').setLevel(logging.ERROR)
        # Add other application loggers here if you want to suppress their warnings in tests:
        # logging.getLogger('business.task_manager_service').setLevel(logging.ERROR)

    # Inform about the mode after logging is set up
    logger = logging.getLogger(__name__)
    logger.debug(f"DEBUG - Logging configured for '{effective_debug_mode}' mode.")

