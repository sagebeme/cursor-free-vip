"""Logging configuration for Cursor Free VIP"""
import logging
import sys
from pathlib import Path
from typing import Optional

# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True
) -> logging.Logger:
    """Setup application-wide logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_console: Whether to enable console logging
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    logger = logging.getLogger('cursor_free_vip')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # If file logging fails, continue with console only
            logger.warning(f"Failed to setup file logging: {e}")
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get the global logger instance, creating it if necessary"""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


# Create default logger instance
logger = get_logger()

