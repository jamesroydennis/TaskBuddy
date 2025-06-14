# taskbuddy_project/config/loguru_setup.py

import os
import sys
from loguru import logger
from config.config import DEBUG_MODE

# Global variable to store the configured debug mode, accessible by filter functions
_current_debug_mode = "dev" # Default, will be set by setup_logging


def setup_logging():
    """
    Configures Loguru's global logger based on application settings,
    including precise custom console colors and CRITICAL background.
    This function should be called once at application startup.
    """
    global _current_debug_mode # Declare intent to modify the global variable

    # Remove all existing handlers to ensure a clean slate on re-configuration
    logger.remove()

    # Get the effective debug mode from config.py and store it globally
    effective_debug_mode = DEBUG_MODE
    _current_debug_mode = effective_debug_mode

    # Define custom formats
    default_console_format = (
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan> | "
        "<level>{message}</level>"
    )
    critical_console_format = (
        "<white on red>{level: <8} | "
        "{name} | "
        "{message}</white on red>"
    )
    file_format = (
        "{level} - {time:YYYY-MM-DD HH:mm:ss.SSS} - {name} - {file}:{line} - {message}"
    )

    # --- Define Loguru's level colors ---
    logger.level("TRACE", color="<black>")
    logger.level("DEBUG", color="<blue>")
    logger.level("INFO", color="<white>")
    logger.level("SUCCESS", color="<green>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<red>")
    logger.level("CRITICAL", color="red")


    # --- Define the console filter function ---
    def console_filter_func(record):
        # 1. Handle messages with specific destinations (from logger.console() or logger.file())
        destination = record.get("extra", {}).get("_destination")
        if destination == "console":  # Always show explicit console messages
            return True
        if destination == "file":  # Never show explicit file messages on console
            return False

        # 2. Handle general logs based on the current debug mode and logger name/level
        if _current_debug_mode == 'test':
            # Allow INFO and higher from test files (those starting with 'test_')
            if record["name"].startswith('test_') and record["level"].no >= logger.level("INFO").no:
                return True
            # For application modules (data, business, core), only allow ERROR or CRITICAL
            if record["name"].startswith(('data.', 'business.', 'core.')):
                return record["level"].no >= logger.level("ERROR").no
            # For other modules (e.g., __main__ from pytest's perspective), allow INFO and higher
            return record["level"].no >= logger.level("INFO").no
        else:
            # In 'dev' or 'prod' mode, allow all (non-destination-specific) messages
            # to pass to the console sink (governed by the sink's level setting, which is TRACE).
            return True


    # --- Add Console Sinks (Handlers) ---

    # 1. Primary Console Sink (filtered by console_filter_func)
    logger.add(
        sys.stderr,
        level="TRACE", # Set level to TRACE to capture all messages for the filter to process
        format=default_console_format,
        colorize=True,
        filter=console_filter_func # Apply our custom filter function
    )

    # 2. Separate Sink for CRITICAL messages ONLY (to ensure full background)
    # This sink's filter takes precedence for CRITICAL records due to order and explicit filter
    logger.add(
        sys.stderr,
        level="CRITICAL", # Only process CRITICAL messages
        format=critical_console_format, # Use the special critical format
        colorize=True,
        # Ensure it also passes our general destination filter (or apply a specific one here if needed)
        filter=lambda record: record["level"].name == "CRITICAL" and (record.get("extra", {}).get("_destination") in (None, "console"))
    )


    # --- Add File Sink (Handler) ---
    if DEBUG_MODE != 'test':
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, 'taskbuddy.log')

        logger.add(
            log_file_path,
            level="DEBUG", # Log all debug messages to file
            format=file_format, # Use simple format for file (no colors in file)
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            filter=lambda record: record.get("extra", {}).get("_destination") in (None, "file")
        )
        logger.info(f"Logging to file: {log_file_path}")

    # --- Custom Logger Methods for Specific Routing ---
    def console_log(message, *args, **kwargs):
        logger.opt(raw=False).info(message, *args, _destination="console", **kwargs)

    def file_log(message, *args, **kwargs):
        logger.opt(raw=False).info(message, *args, _destination="file", **kwargs)

    logger.console = console_log
    logger.file = file_log

    # --- Suppress Loguru's internal logs when running tests for cleaner output ---
    if DEBUG_MODE == 'test':
        logger.disable("loguru")

    logger.info(f"Loguru setup complete. Running in {DEBUG_MODE} mode.")
    logger.file(f"[FILE_ONLY] Loguru setup complete. Running in {DEBUG_MODE} mode.")

# Call setup_logging so it configures Loguru upon import
setup_logging()
