"""
Utility functions for StratScout backend services.
"""
import hashlib
import json
import time
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from functools import wraps


def generate_hash(data: str) -> str:
    """
    Generate SHA-256 hash for deduplication.
    
    Args:
        data: String data to hash
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def generate_id(prefix: str, *parts: str) -> str:
    """
    Generate unique ID with prefix.
    
    Args:
        prefix: ID prefix (e.g., 'comp', 'ad', 'analysis')
        *parts: Additional parts to include in ID
    
    Returns:
        Unique ID string
    """
    timestamp = str(int(time.time() * 1000))
    hash_input = '-'.join([timestamp] + list(parts))
    hash_suffix = generate_hash(hash_input)[:8]
    return f"{prefix}-{timestamp}-{hash_suffix}"


def get_current_timestamp() -> int:
    """Get current Unix timestamp in milliseconds."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def get_ttl(days: int = 90) -> int:
    """
    Get TTL timestamp for DynamoDB.
    
    Args:
        days: Number of days until expiration
    
    Returns:
        Unix timestamp for TTL
    """
    return int(time.time()) + (days * 24 * 60 * 60)


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.
    
    Args:
        data: JSON string
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = '{}') -> str:
    """
    Safely serialize to JSON string.
    
    Args:
        data: Data to serialize
        default: Default value if serialization fails
    
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_multiplier: Multiplier for exponential backoff
        jitter: Whether to add random jitter
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import random
            
            attempt = 0
            delay = base_delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    
                    # Calculate delay with exponential backoff
                    current_delay = min(delay * (backoff_multiplier ** (attempt - 1)), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        current_delay *= (0.5 + random.random())
                    
                    time.sleep(current_delay)
            
            return None
        
        return wrapper
    return decorator


def chunk_list(items: list, chunk_size: int) -> list:
    """
    Split list into chunks.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def normalize_text(text: str) -> str:
    """
    Normalize text for analysis.
    
    Args:
        text: Input text
    
    Returns:
        Normalized text
    """
    if not text:
        return ''
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Convert to lowercase for consistency
    text = text.lower()
    
    return text.strip()


def calculate_confidence_score(
    factors: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate weighted confidence score.
    
    Args:
        factors: Dictionary of factor names to scores (0-1)
        weights: Optional dictionary of factor weights (default: equal weights)
    
    Returns:
        Weighted confidence score (0-1)
    """
    if not factors:
        return 0.0
    
    if weights is None:
        weights = {k: 1.0 for k in factors.keys()}
    
    total_weight = sum(weights.get(k, 1.0) for k in factors.keys())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(
        factors[k] * weights.get(k, 1.0)
        for k in factors.keys()
    )
    
    return min(max(weighted_sum / total_weight, 0.0), 1.0)
