"""
Logger adapter - Implementation of Logger port.
"""

import logging
import sys
from pathlib import Path

from src.application.ports.interfaces import Logger as LoggerPort


class LoggerAdapter(LoggerPort):
    """Adapter for logging operations."""
    
    def __init__(self, name: str, log_file: str = "app.log", level: str = "INFO"):
        self._logger = logging.getLogger(name)
        self._setup_logging(log_file, level)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self._logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self._logger.debug(message)
    
    def _setup_logging(self, log_file: str, level: str) -> None:
        """Configure logging for the application."""
        # Set logging level
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(numeric_level)
        
        # Only add handlers if they don't exist (avoid duplicates)
        if not self._logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
            
            # File handler
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(numeric_level)
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)
            except Exception as e:
                # If file handler fails, log to console only
                self._logger.warning(f"Failed to create file handler: {e}")
        
        # Prevent propagation to avoid duplicate logs
        self._logger.propagate = False