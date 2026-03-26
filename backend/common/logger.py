"""
Logging configuration for StratScout backend services.
"""
import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def get_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Log message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **kwargs: Additional context fields
    """
    extra = {'extra_fields': kwargs}
    getattr(logger, level.lower())(message, extra=extra)
