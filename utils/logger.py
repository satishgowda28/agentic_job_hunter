# utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Base configuration
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Default to INFO

    # Formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler (prints to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File Handler (saves to file, rotates when it hits 5MB)
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)

    # Attach handlers (prevent duplicates)
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
