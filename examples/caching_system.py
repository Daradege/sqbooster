"""
Caching System Example - sqbooster

This example demonstrates how to implement a caching system using sqbooster
with different storage backends and cache strategies.
"""

import time
import hashlib
import json
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from sqbooster.databases import SQLiteDatabase, JSONFileDatabase

class CacheManager:
    """A flexible caching system using sqbooster."""
    
    def __init__(self, backend="sqlite", cache_file="examples/cache"):
        """Initialize the cache manager with specified backend."""
        if backend == "sqlite":
            self.db = SQLiteDatabase(f"{cache_file}.db")
        elif backend == "json":
            self.db = JSONFileDatabase(f"{cache_file}.json")
        else:
            raise ValueError("Unsupported backend. Use 'sqlite' or 'json'")
        
        self.backend = backend
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate a namespaced cache key."""
        return f"{namespace}:{key}"
    
    def _is_expired(self, cache_entry: dict) -> bool:
        """Check if a cache entry has expired."""
        if "expires_at" not in cache_entry:
            return False
        
        expires_at = datetime.fromisoformat(cache_entry["expires_at"])
        return datetime.now() > expires_at
    
    def set(self, key: str, value: Any, ttl: int = 3600, namespace: str = "default"):
        """Set a value in the cache with optional TTL (time to live) in seconds."""
        cache_key = self._generate_key(key, namespace)
        
        cache_entry = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat(),
            "hit_count": 0
        }
        
        self.db.write(cache_key, cache_entry)
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get a value from the cache."""
        cache_key = self._generate_key(key, namespace)
        
        if not self.db.exists(cache_key):
            return None
        
        cache_entry = self.db.read(cache_key)
        
        # Check if expired
        if self._is_expired(cache_entry):
            self.db.delete(cache_key)
            return None
        
        # Update hit count
        cache_entry["hit_count"] += 1
        cache_entry["last_accessed"] = datetime.now().isoformat()
        self.db.write(cache_key, cache_entry)
        
        return cache_entry["value"]
    
    def delete(self, key: str, namespace: str = "default"):
        """Delete a key from the cache."""
        cache_key = self._generate_key(key, namespace)
        self.db.delete(cache_key)
    
    def clear_namespace(self, namespace: str = "default"):
        """Clear all keys in a namespace (simplified implementation)."""
        # Note: This is a basic implementation. In production, you'd want
        # a more efficient way to iterate through keys by namespace
        pass
    
    def get_stats(self, key: str, namespace: str = "default") -> Optional[dict]:
        """Get cache statistics for a key."""
        cache_key = self._generate_key(key, namespace)
        
        if not self.db.exists(cache_key):
            return None
        
        cache_entry = self.db.read(cache_key)
        
        return {
            "created_at": cache_entry.get("created_at"),
            "expires_at": cache_entry.get("expires_at"),
            "hit_count": cache_entry.get("hit_count", 0),
            "last_accessed": cache_entry.get("last_accessed"),
            "is_expired": self._is_expired(cache_entry)
        }

def cache_decorator(cache_manager: CacheManager, ttl: int = 3600, namespace: str = "functions"):
    """Decorator to cache function results."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key_data = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            key = hashlib.md5(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(key, namespace)
            if cached_result is not None:
                print(f"Cache HIT for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            print(f"Cache MISS for {func.__name__}")
            result = func(*args, **kwargs)
            cache_manager.set(key, result, ttl, namespace)
            return result
        
        return wrapper
    return decorator

# Example functions to demonstrate caching
def expensive_computation(n: int) -> int:
    """Simulate an expensive computation."""
    print(f"Performing expensive computation for n={n}")
    time.sleep(2)  # Simulate work
    return sum(i * i for i in range(n))

def fetch_user_data(user_id: int) -> dict:
    """Simulate fetching user data from an API."""
    print(f"Fetching user data for user_id={user_id}")
    time.sleep(1)  # Simulate network delay
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": datetime.now().isoformat()
    }

def main():
    print("=== Caching System Example ===\n")
    
    # Test with SQLite backend
    print("--- SQLite Cache Backend ---")
    sqlite_cache = CacheManager("sqlite", "examples/sqlite_cache")
    
    # Basic caching operations
    print("Setting cache values...")
    sqlite_cache.set("user:123", {"name": "Alice", "age": 30}, ttl=10)
    sqlite_cache.set("config:app", {"theme": "dark", "lang": "en"}, ttl=60)
    
    print("Getting cache values...")
    user_data = sqlite_cache.get("user:123")
    config_data = sqlite_cache.get("config:app")
    print(f"User data: {user_data}")
    print(f"Config data: {config_data}")
    
    # Cache statistics
    print("\nCache statistics:")
    user_stats = sqlite_cache.get_stats("user:123")
    print(f"User cache stats: {user_stats}")
    
    # Test with JSON backend
    print("\n--- JSON Cache Backend ---")
    json_cache = CacheManager("json", "examples/json_cache")
    
    # Function caching with decorator
    print("\n--- Function Caching ---")
    
    # Create cached versions of functions
    cached_computation = cache_decorator(json_cache, ttl=30, namespace="math")(expensive_computation)
    cached_user_fetch = cache_decorator(json_cache, ttl=60, namespace="api")(fetch_user_data)
    
    # First calls (cache miss)
    print("First calls (should be slow):")
    result1 = cached_computation(100)
    user1 = cached_user_fetch(123)
    print(f"Computation result: {result1}")
    print(f"User data: {user1}")
    
    # Second calls (cache hit)
    print("\nSecond calls (should be fast):")
    result2 = cached_computation(100)
    user2 = cached_user_fetch(123)
    print(f"Computation result: {result2}")
    print(f"User data: {user2}")
    
    # Namespace-based caching
    print("\n--- Namespace-based Caching ---")
    
    # Cache data in different namespaces
    json_cache.set("temp_data", "This is temporary", ttl=5, namespace="temp")
    json_cache.set("temp_data", "This is permanent", ttl=3600, namespace="permanent")
    
    print("Temporary data:", json_cache.get("temp_data", "temp"))
    print("Permanent data:", json_cache.get("temp_data", "permanent"))
    
    # Wait for temporary data to expire
    print("\nWaiting 6 seconds for temporary data to expire...")
    time.sleep(6)
    
    print("After expiration:")
    print("Temporary data:", json_cache.get("temp_data", "temp"))
    print("Permanent data:", json_cache.get("temp_data", "permanent"))
    
    # Cache performance comparison
    print("\n--- Performance Comparison ---")
    
    # Without cache
    start_time = time.time()
    for i in range(3):
        expensive_computation(50)
    no_cache_time = time.time() - start_time
    
    # With cache
    start_time = time.time()
    for i in range(3):
        cached_computation(50)
    with_cache_time = time.time() - start_time
    
    print(f"Without cache: {no_cache_time:.2f} seconds")
    print(f"With cache: {with_cache_time:.2f} seconds")
    print(f"Speed improvement: {no_cache_time / with_cache_time:.2f}x")
    
    print("\nCaching system example completed!")

if __name__ == "__main__":
    main()
