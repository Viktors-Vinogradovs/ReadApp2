"""Centralized logging configuration.

Replaces scattered print() statements with structured logging.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string (None = use default)
        include_timestamp: Include timestamp in logs
        
    Example:
        >>> setup_logging(level="DEBUG")
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        else:
            format_string = "[%(levelname)s] %(name)s: %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    return logging.getLogger(name)


# Emoji prefixes for different log levels (optional, for readability)
LOG_EMOJIS = {
    "DEBUG": "🔍",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🔥",
}


def log_with_emoji(logger: logging.Logger, level: str, message: str, *args, **kwargs):
    """
    Log message with emoji prefix for better visual scanning.
    
    Args:
        logger: Logger instance
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message (supports % formatting)
        *args: Format arguments
        **kwargs: Additional logging kwargs
        
    Example:
        >>> log_with_emoji(logger, "INFO", "User %s logged in", "john@example.com")
    """
    emoji = LOG_EMOJIS.get(level.upper(), "")
    formatted_message = f"{emoji} {message}" if emoji else message
    
    log_method = getattr(logger, level.lower())
    log_method(formatted_message, *args, **kwargs)

