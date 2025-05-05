import functools
import time
from typing import Dict, Any, Optional

class JokeCache:
    """
    A thread-safe, time-based cache for storing and retrieving jokes.
    
    The cache allows setting a maximum number of jokes and a time-to-live (TTL)
    for each cached joke to prevent stale content.
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        Initialize the JokeCache.
        
        Args:
            max_size (int): Maximum number of jokes to store in the cache. Defaults to 100.
            ttl (int): Time-to-live in seconds for each cached joke. Defaults to 1 hour.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a joke from the cache if it exists and is not expired.
        
        Args:
            key (str): Unique identifier for the joke.
        
        Returns:
            Optional[str]: The joke if found and not expired, else None.
        """
        if key in self._cache:
            cache_entry = self._cache[key]
            current_time = time.time()
            
            if current_time - cache_entry['timestamp'] < self._ttl:
                return cache_entry['joke']
            
            # Remove expired entry
            del self._cache[key]
        
        return None
    
    def set(self, key: str, joke: str) -> None:
        """
        Add a joke to the cache.
        
        If the cache is full, the least recently added joke will be removed.
        
        Args:
            key (str): Unique identifier for the joke.
            joke (str): The joke text to cache.
        """
        current_time = time.time()
        
        # Remove expired entries
        self._cache = {
            k: v for k, v in self._cache.items()
            if current_time - v['timestamp'] < self._ttl
        }
        
        # If cache is full, remove the oldest entry
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
        
        self._cache[key] = {
            'joke': joke,
            'timestamp': current_time
        }
    
    def clear(self) -> None:
        """
        Clear all entries from the cache.
        """
        self._cache.clear()
    
    def __len__(self) -> int:
        """
        Get the current number of jokes in the cache.
        
        Returns:
            int: Number of cached jokes.
        """
        return len(self._cache)

def cached_joke(cache: Optional[JokeCache] = None):
    """
    A decorator to cache jokes retrieved by a function.
    
    Args:
        cache (Optional[JokeCache]): A JokeCache instance to use. If not provided,
                                     a default cache will be created.
    
    Returns:
        Callable: A decorator function for caching jokes.
    """
    if cache is None:
        cache = JokeCache()
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, key: Optional[str] = None, **kwargs):
            if key is None:
                key = str(args) + str(kwargs)
            
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    
    return decorator