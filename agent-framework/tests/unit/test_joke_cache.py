import time
import pytest
from prometheus_swarm.utils.joke_cache import JokeCache, cached_joke

def test_joke_cache_basic_functionality():
    """Test basic caching and retrieval of jokes."""
    cache = JokeCache(max_size=3, ttl=10)
    
    cache.set('joke1', 'Why did the chicken cross the road?')
    cache.set('joke2', 'Why did the programmer quit his job?')
    
    assert cache.get('joke1') == 'Why did the chicken cross the road?'
    assert cache.get('joke2') == 'Why did the programmer quit his job?'
    assert len(cache) == 2

def test_joke_cache_max_size():
    """Test that the cache respects the maximum size limit."""
    cache = JokeCache(max_size=2, ttl=10)
    
    cache.set('joke1', 'Joke 1')
    cache.set('joke2', 'Joke 2')
    cache.set('joke3', 'Joke 3')
    
    assert cache.get('joke1') is None  # First joke should be evicted
    assert cache.get('joke2') == 'Joke 2'
    assert cache.get('joke3') == 'Joke 3'
    assert len(cache) == 2

def test_joke_cache_ttl():
    """Test that jokes expire after their time-to-live."""
    cache = JokeCache(max_size=3, ttl=1)
    
    cache.set('joke1', 'Time-sensitive joke')
    assert cache.get('joke1') == 'Time-sensitive joke'
    
    time.sleep(1.1)  # Wait slightly longer than TTL
    assert cache.get('joke1') is None

def test_cached_joke_decorator():
    """Test the cached_joke decorator."""
    call_count = 0
    
    @cached_joke()
    def get_joke(topic):
        nonlocal call_count
        call_count += 1
        return f"A {topic} joke"
    
    # First call should compute and cache
    joke1 = get_joke('programming')
    assert joke1 == 'A programming joke'
    assert call_count == 1
    
    # Second call should return cached result
    joke2 = get_joke('programming')
    assert joke2 == 'A programming joke'
    assert call_count == 1  # Should not increment
    
    # Different topic should trigger a new computation
    joke3 = get_joke('math')
    assert joke3 == 'A math joke'
    assert call_count == 2

def test_cached_joke_custom_cache():
    """Test using a custom cache with the decorator."""
    custom_cache = JokeCache(max_size=1, ttl=5)
    
    @cached_joke(custom_cache)
    def get_joke(topic):
        return f"A {topic} joke"
    
    joke1 = get_joke('programming')
    joke2 = get_joke('math')
    
    assert custom_cache.get('(\'programming\',){}') is None  # Evicted by max_size
    assert custom_cache.get('(\'math\',){}') == 'A math joke'

def test_joke_cache_clear():
    """Test clearing the entire cache."""
    cache = JokeCache(max_size=3, ttl=10)
    
    cache.set('joke1', 'Joke 1')
    cache.set('joke2', 'Joke 2')
    
    assert len(cache) == 2
    cache.clear()
    assert len(cache) == 0