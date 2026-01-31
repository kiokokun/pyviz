import logging
import logging.handlers
import os

LOG_FILE = "pyviz.log"

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Check if handlers already exist to avoid duplicates
    if not logger.handlers:
        # File Handler with Rotation (max 5MB, 3 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=3
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # We generally don't want to log to stdout/stderr in the Engine because
        # it might interfere with the TUI or piped output, but for debugging we might.
        # Since we use Rich for rendering, simple prints break the UI.
        # So we stick to file logging primarily.

    return logger
