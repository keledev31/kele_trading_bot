"""
Logging configuration for MeshTradeBot.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = "./logs"


def setup_logging(name: str, log_file: str = None):
    """
    Setup logger with both file and console handlers.
    Logs to JSON format for better parsing.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional custom log file path
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Default log file
    if log_file is None:
        log_file = os.path.join(LOG_DIR, f"{name.replace('.', '_')}.log")
    
    # File handler with rotation (10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
