"""
The `sqbooster.databases.picklefile` module provides a file-based database implementation using Python's pickle serialization.
The `PickleFileDatabase` class provides methods to interact with a pickle file as a key-value store.
It allows reading, writing, and deleting key-value pairs, as well as retrieving all keys.
"""

from ...exceptions import ConnectionError, SerializationError, DatabaseError
import sqlite3
from typing import Any, Dict, List
import json
import os

class SQLiteDatabase:
    """A SQLite database implementation for key-value storage.

    This class provides methods to interact with a SQLite database for storing
    and retrieving key-value pairs with automatic serialization of values.

    Args:
        name (str): The name/path of the SQLite database file.
        auto_commit (bool, optional): Whether to automatically commit changes. Defaults to True.

    Raises:
        ConnectionError: If database initialization fails.
    """

    def __init__(self, name: str, auto_commit: bool = True):
        """Initialize database with options for auto-commit and in-memory storage.

        Args:
            name (str): The name/path of the SQLite database file.
            auto_commit (bool, optional): Whether to automatically commit changes. Defaults to True.

        Raises:
            ConnectionError: If database initialization fails.
        """
        self.name = name
        self.auto_commit = auto_commit
        try:
            self.conn = sqlite3.connect(self.name)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS data
                              (key TEXT PRIMARY KEY, value TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to initialize database: {str(e)}")
    
    def read(self, key: str, default: Any = None) -> Any:
        """Read a value from the database by its key.

        Args:
            key (str): The key to look up.
            default (Any, optional): Default value if key doesn't exist. Defaults to None.

        Returns:
            Any: The value associated with the key, or the default value if not found.

        Raises:
            DatabaseError: If the read operation fails.
        """
        try:
            self.cursor.execute("SELECT value FROM data WHERE key=?", (key,))
            result = self.cursor.fetchone()
            if result:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return result[0]
            return default
        except sqlite3.OperationalError as e:
            raise DatabaseError(f"Failed to read from database: {str(e)}")
    
    def write(self, key: str, value: Any, commit: bool = None) -> bool:
        """Write a key-value pair to the database.

        Args:
            key (str): The key to store the value under.
            value (Any): The value to store.
            commit (bool, optional): Whether to commit the change. If None, uses auto_commit setting.

        Returns:
            bool: True if write operation was successful.

        Raises:
            SerializationError: If value serialization fails.
            DatabaseError: If the write operation fails.
        """
        try:
            value_json = json.dumps(value)
            self.cursor.execute("INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)", 
                              (key, value_json))
            if commit or (commit is None and self.auto_commit):
                self.conn.commit()
            return True
        except json.JSONDecodeError as e:
            raise SerializationError(f"Failed to serialize value: {str(e)}")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to write to database: {str(e)}")
    
    def keys(self, pattern: str = None) -> List[str]:
        """Get all keys in the database, optionally filtered by pattern.

        Args:
            pattern (str, optional): Pattern to filter keys. Defaults to None.

        Returns:
            List[str]: List of matching keys.

        Raises:
            DatabaseError: If the key fetch operation fails.
        """
        try:
            if pattern:
                self.cursor.execute("SELECT key FROM data WHERE key LIKE ?", (f"%{pattern}%",))
            else:
                self.cursor.execute("SELECT key FROM data")
            return [key[0] for key in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch keys: {str(e)}")
    
    def delete_key(self, key: str, commit: bool = None) -> bool:
        """Delete a specific key from the database.

        Args:
            key (str): The key to delete.
            commit (bool, optional): Whether to commit the change. If None, uses auto_commit setting.

        Returns:
            bool: True if deletion was successful.

        Raises:
            DatabaseError: If the deletion operation fails.
        """
        try:
            self.cursor.execute("DELETE FROM data WHERE key=?", (key,))
            if commit or (commit is None and self.auto_commit):
                self.conn.commit()
            return True
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete key: {str(e)}")
    
    def delete_database(self, commit: bool = None) -> bool:
        """Delete all data from the database.

        Args:
            commit (bool, optional): Whether to commit the change. If None, uses auto_commit setting.

        Returns:
            bool: True if database deletion was successful.

        Raises:
            DatabaseError: If the database deletion fails.
        """
        try:
            self.cursor.execute("DELETE FROM data")
            if commit or (commit is None and self.auto_commit):
                self.conn.commit()
            return True
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete database: {str(e)}")
    
    def close(self) -> None:
        """Close the database connection.

        Raises:
            ConnectionError: If closing the connection fails.
        """
        try:
            self.conn.close()
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to close database: {str(e)}")
    
    def remove_database(self) -> bool:
        """Remove the database file from the filesystem.

        Returns:
            bool: True if file removal was successful.

        Raises:
            DatabaseError: If removing the database file fails.
        """
        try:
            self.close()
            os.remove(self.name)
            return True
        except OSError as e:
            raise DatabaseError(f"Failed to remove database file: {str(e)}")
    
    def get_size(self) -> int:
        """Get the number of key-value pairs in the database.

        Returns:
            int: Number of entries in the database.

        Raises:
            DatabaseError: If getting the size fails.
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM data")
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get database size: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in the database.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.

        Raises:
            DatabaseError: If checking key existence fails.
        """
        try:
            self.cursor.execute("SELECT 1 FROM data WHERE key=?", (key,))
            return bool(self.cursor.fetchone())
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to check key existence: {str(e)}")