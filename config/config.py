# taskbuddy_project/config.py

import logging

# --- Application-wide Configuration ---

# Debug Mode:
# 'dev': Development mode (most verbose logging, specific dev features)
# 'test': Testing mode (often minimal output, specific test configurations)
# 'prod': Production mode (minimal logging, optimized performance, secure settings)
DEBUG_MODE = 'dev' # Change this based on your current environment

# --- Logging Configuration ---
# Logging level will be set based on DEBUG_MODE
# Possible levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

if DEBUG_MODE == 'dev':
    LOGGING_LEVEL = logging.DEBUG
elif DEBUG_MODE == 'test':
    LOGGING_LEVEL = logging.INFO # Or logging.DEBUG if test output is desired
elif DEBUG_MODE == 'prod':
    LOGGING_LEVEL = logging.WARNING # Only warnings and errors in production
else:
    LOGGING_LEVEL = logging.INFO # Default if DEBUG_MODE is unrecognised


# --- Other potential future configurations ---
# DATABASE_URL = "sqlite:///data/taskbuddy.db"
# API_KEY = "your_api_key_here" # Example for future API integration
# MEMO_AUDIO_FORMAT = "wav" # Example for future audio memo settings