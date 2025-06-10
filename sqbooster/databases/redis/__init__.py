"""
This module provides a Redis database connection for sqbooster.
The RedisDatabase class provides methods to interact with a Redis database.
It allows reading, writing, and deleting key-value pairs, as well as retrieving all keys.
"""

from ...exceptions import ConnectionError,DatabaseError,KeyNotFoundError,SerializationError
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

try:
    import redis
    
    class RedisDatabase:
        """Redis database connection handler.
        
        This class provides methods to interact with a Redis database, including reading,
        writing, and managing key-value pairs.
        
        Args:
            name (str, optional): Database name or number. Defaults to "db".
            host (str, optional): Redis server host. Defaults to "localhost".
            port (int, optional): Redis server port. Defaults to 6379.
            password (str, optional): Redis server password. Defaults to None.
            auto_commit (bool, optional): Auto commit flag. Defaults to True.
            
        Raises:
            ConnectionError: If connection to Redis server fails.
        """
        
        def __init__(self, name: str = "db", host: str = "localhost", port: int = 6379, 
                     password: str = None, auto_commit: bool = True):
            """Initialize Redis database connection"""
            self.name = name
            self.auto_commit = auto_commit
            try:
                self.conn = redis.Redis(host=host, port=port, password=password, 
                                      decode_responses=True, db=int(name) if name.isdigit() else 0)
                self.conn.ping()  # Test connection
            except redis.RedisError as e:
                raise ConnectionError(f"Failed to connect to Redis: {str(e)}")
        
        def read(self, key: str, default: Any = None) -> Any:
            """Read value from Redis by key.
            
            Args:
                key (str): Key to read.
                default (Any, optional): Default value if key not found. Defaults to None.
                
            Returns:
                Any: Value associated with the key or default if not found.
                
            Raises:
                DatabaseError: If reading from Redis fails.
            """
            try:
                result = self.conn.get(key)
                if result:
                    try:
                        return json.loads(result)
                    except json.JSONDecodeError:
                        return result
                return default
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to read from Redis: {str(e)}")
        
        def write(self, key: str, value: Any, commit: bool = None) -> bool:
            """Write key-value pair to Redis.
            
            Args:
                key (str): Key to write.
                value (Any): Value to store.
                commit (bool, optional): Override auto_commit setting. Defaults to None.
                
            Returns:
                bool: True if write successful.
                
            Raises:
                SerializationError: If value serialization fails.
                DatabaseError: If writing to Redis fails.
            """
            try:
                value_json = json.dumps(value)
                self.conn.set(key, value_json)
                # Set creation timestamp
                self.conn.set(f"{key}:created_at", datetime.now().isoformat())
                return True
            except json.JSONDecodeError as e:
                raise SerializationError(f"Failed to serialize value: {str(e)}")
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to write to Redis: {str(e)}")
        
        def keys(self, pattern: str = None) -> List[str]:
            """Get all keys matching pattern.
            
            Args:
                pattern (str, optional): Pattern to match keys. Defaults to None.
                
            Returns:
                List[str]: List of matching keys.
                
            Raises:
                DatabaseError: If fetching keys fails.
            """
            try:
                if pattern:
                    keys = self.conn.keys(f"*{pattern}*")
                else:
                    keys = self.conn.keys("*")
                # Filter out timestamp keys
                return [k for k in keys if not k.endswith(":created_at")]
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to fetch keys: {str(e)}")
        
        def delete_key(self, key: str, commit: bool = None) -> bool:
            """Delete key from Redis.
            
            Args:
                key (str): Key to delete.
                commit (bool, optional): Override auto_commit setting. Defaults to None.
                
            Returns:
                bool: True if deletion successful.
                
            Raises:
                DatabaseError: If key deletion fails.
            """
            try:
                self.conn.delete(key, f"{key}:created_at")
                return True
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to delete key: {str(e)}")
        
        def delete_database(self, commit: bool = None) -> bool:
            """Delete all keys in the database.
            
            Args:
                commit (bool, optional): Override auto_commit setting. Defaults to None.
                
            Returns:
                bool: True if database deletion successful.
                
            Raises:
                DatabaseError: If database deletion fails.
            """
            try:
                self.conn.flushdb()
                return True
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to delete database: {str(e)}")
        
        def close(self) -> None:
            """Close Redis connection.
            
            Raises:
                ConnectionError: If closing connection fails.
            """
            try:
                self.conn.close()
            except redis.RedisError as e:
                raise ConnectionError(f"Failed to close Redis connection: {str(e)}")
        
        def get_size(self) -> int:
            """Get number of keys in database.
            
            Returns:
                int: Number of keys in database.
                
            Raises:
                DatabaseError: If getting size fails.
            """
            try:
                return len([k for k in self.conn.keys("*") if not k.endswith(":created_at")])
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to get database size: {str(e)}")
        
        def exists(self, key: str) -> bool:
            """Check if key exists in database.
            
            Args:
                key (str): Key to check.
                
            Returns:
                bool: True if key exists, False otherwise.
                
            Raises:
                DatabaseError: If checking key existence fails.
            """
            try:
                return bool(self.conn.exists(key))
            except redis.RedisError as e:
                raise DatabaseError(f"Failed to check key existence: {str(e)}")

except ImportError:
    class RedisDatabase:
        """Fallback class when Redis is not installed."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Redis library not installed. Install with: pip install redis")