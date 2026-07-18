"""Unified project logging framework."""

import logging
import sys
from pathlib import Path
from typing import Optional

# Default logging level for development/production debugging
DEFAULT_LEVEL = logging.DEBUG


def setup_logger(
    name: str = "txt_to_docx",
    level: int = DEFAULT_LEVEL,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configures and returns a new logger equipped with optimal standard handlers.

    Args:
        name: Name of the logger.
        level: Logging severity threshold (e.g., logging.DEBUG, logging.INFO).
        log_file: Optional path to save logs to a physical file.

    Returns:
        The configured logging.Logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if the logger is already initialized
    if logger.handlers:
        return logger

    # Log message structural format
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console Handler (Stdout output stream)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Optional persistent storage)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Retrieves a contextual child logger for a specific application module.

    Args:
        name: Name of the module/sub-component.

    Returns:
        The scoped child Logger instance.
    """
    # Ensure the root package logger is configured first
    root_logger = logging.getLogger("txt_to_docx")
    if not root_logger.handlers:
        setup_logger()

    # Apply proper naming hierarchy convention
    child_name = f"txt_to_docx.{name}" if not name.startswith("txt_to_docx.") else name
    return logging.getLogger(child_name)