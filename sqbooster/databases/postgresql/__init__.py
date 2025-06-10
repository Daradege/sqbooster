"""
This module provides a PostgreSQL database implementation.
The PostgreSQLDatabase class provides methods to interact with a PostgreSQL database.
It allows reading, writing, and deleting key-value pairs, as well as retrieving all keys.
"""

from ...exceptions import ConnectionError,DatabaseError,KeyNotFoundError,SerializationError
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

try:
    import psycopg2
    from psycopg2.extras import Json
    
    class PostgreSQLDatabase:
        def __init__(self, name: str = "testdb", host: str = "localhost", port: int = 5432,
                     user: str = "postgres", password: str = "", auto_commit: bool = True):
            """Initialize PostgreSQL connection.

            Args:
                name (str, optional): Database name. Defaults to "testdb".
                host (str, optional): Database host. Defaults to "localhost".
                port (int, optional): Database port. Defaults to 5432.
                user (str, optional): Database user. Defaults to "postgres".
                password (str, optional): Database password. Defaults to "".
                auto_commit (bool, optional): Auto commit flag. Defaults to True.

            Raises:
                ConnectionError: If connection to PostgreSQL fails.
            """
            self.name = name
            self.auto_commit = auto_commit
            try:
                self.conn = psycopg2.connect(
                    host=host, port=port, database=name, user=user, password=password
                )
                self.cursor = self.conn.cursor()
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS data
                                  (key VARCHAR PRIMARY KEY, value JSONB, 
                                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                self.conn.commit()
            except psycopg2.Error as e:
                raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
        
        def read(self, key: str, default: Any = None) -> Any:
            """Read value from database by key.

            Args:
                key (str): Key to read.
                default (Any, optional): Default value if key not found. Defaults to None.

            Returns:
                Any: Value associated with the key.

            Raises:
                DatabaseError: If reading from PostgreSQL fails.
            """
            try:
                self.cursor.execute("SELECT value FROM data WHERE key=%s", (key,))
                result = self.cursor.fetchone()
                return result[0] if result else default
            except psycopg2.Error as e:
                raise DatabaseError(f"Failed to read from PostgreSQL: {str(e)}")
        
        def write(self, key: str, value: Any, commit: bool = None) -> bool:
            """Write key-value pair to database.

            Args:
                key (str): Key to write.
                value (Any): Value to write.
                commit (bool, optional): Force commit operation. Defaults to None.

            Returns:
                bool: True if write successful.

            Raises:
                DatabaseError: If writing to PostgreSQL fails.
            """
            try:
                self.cursor.execute("INSERT INTO data (key, value) VALUES (%s, %s) "
                                  "ON CONFLICT (key) DO UPDATE SET value = %s", 
                                  (key, Json(value), Json(value)))
                if commit or (commit is None and self.auto_commit):
                    self.conn.commit()
                return True
            except psycopg2.Error as e:
                raise DatabaseError(f"Failed to write to PostgreSQL: {str(e)}")
        
        def keys(self, pattern: str = None) -> List[str]:
            """Get all keys or keys matching pattern.

            Args:
                pattern (str, optional): Pattern to match keys. Defaults to None.

            Returns:
                List[str]: List of matching keys.

            Raises:
                DatabaseError: If fetching keys fails.
            """
            try:
                if pattern:
                    self.cursor.execute("SELECT key FROM data WHERE key LIKE %s", (f"%{pattern}%",))
                else:
                    self.cursor.execute("SELECT key FROM data")
                return [key[0] for key in self.cursor.fetchall()]
            except psycopg2.Error as e:
                raise DatabaseError(f"Failed to fetch keys: {str(e)}")
        
        def delete_key(self, key: str, commit: bool = None) -> bool:
            """Delete a key from database.

            Args:
                key (str): Key to delete.
                commit (bool, optional): Force commit operation. Defaults to None.

            Returns:
                bool: True if deletion successful.

            Raises:
                DatabaseError: If deleting key fails.
            """
            try:
                self.cursor.execute("DELETE FROM data WHERE key=%s", (key,))
                if commit or (commit is None and self.auto_commit):
                    self.conn.commit()
                return True
            except psycopg2.Error as e:
                raise DatabaseError(f"Failed to delete key: {str(e)}")
        
        def delete_database(self, commit: bool = None) -> bool:
            """Delete all data from database.

            Args:
                commit (bool, optional): Force commit operation. Defaults to None.

            Returns:
                bool: True if deletion successful.

            Raises:
                DatabaseError: If deleting database fails.
            """
            try:
                self.cursor.execute("DELETE FROM data")
                if commit or (commit is None and self.auto_commit):
                    self.conn.commit()
                return True
            except psycopg2.Error as e:
                raise DatabaseError(f"Failed to delete database: {str(e)}")
        
        def close(self) -> None:
            """Close database connection.

            Raises:
                ConnectionError: If closing connection fails.
            """
            try:
                self.conn.close()
            except psycopg2.Error as e:
                raise ConnectionError(f"Failed to close PostgreSQL connection: {str(e)}")
        
        def get_size(self) -> int:
            """Get number of key-value pairs in database.

            Returns:
                int: Number of entries in database.

            Raises:
                DatabaseError: If getting database size fails.
            """
            try:
                self.cursor.execute("SELECT COUNT(*) FROM data")
                return self.cursor.fetchone()[0]
            except psycopg2.Error as e:
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
                self.cursor.execute("SELECT 1 FROM data WHERE key=%s", (key,))
                return bool(self.cursor.fetchone())
            except psycopg2.Error as e:
                raise DatabaseError(f"Failed to check key existence: {str(e)}")

except ImportError:
    class PostgreSQLDatabase:
        def __init__(self, *args, **kwargs):
            raise ImportError("Psycopg2 library not installed. Install with: pip install psycopg2-binary")