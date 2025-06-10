"""
This module provides a file-based database implementation using Python's pickle serialization.
The PickleFileDatabase class provides methods to interact with a pickle file as a key-value store.
It allows reading, writing, and deleting key-value pairs, as well as retrieving all keys.
"""

from ...exceptions import ConnectionError,DatabaseError,KeyNotFoundError,SerializationError
from typing import Any, List
import os
from datetime import datetime
import pickle

class PickleFileDatabase:
    """A file-based database implementation using Python's pickle serialization.

    This class provides a simple key-value store backed by a pickle file on disk.
    It supports basic CRUD operations and maintains timestamps for each entry.

    Args:
        name (str): The filename for the pickle database. Defaults to "database.pkl".
        auto_commit (bool): Whether to automatically save changes to disk. Defaults to True.

    Attributes:
        name (str): The filename of the database.
        auto_commit (bool): Flag indicating if changes should be automatically saved.
        data (dict): The main data store containing key-value pairs.
        timestamps (dict): Stores timestamps for each key in the database.
    """

    def __init__(self, name: str = "database.pkl", auto_commit: bool = True):
        """Initialize file-based Pickle database.

        Args:
            name (str): The filename for the pickle database.
            auto_commit (bool): Whether to automatically save changes to disk.

        Raises:
            ConnectionError: If there's an error initializing the database file.
        """
        self.name = name
        self.auto_commit = auto_commit
        self.data = {}
        self.timestamps = {}
        try:
            if os.path.exists(name):
                with open(name, 'rb') as f:
                    file_data = pickle.load(f)
                    self.data = file_data.get('data', {})
                    self.timestamps = file_data.get('timestamps', {})
        except (pickle.PickleError, IOError) as e:
            raise ConnectionError(f"Failed to initialize Pickle database: {str(e)}")
    
    def _save_to_file(self):
        """Save the current state of the database to disk.

        Raises:
            DatabaseError: If there's an error saving to the file.
        """
        try:
            with open(self.name, 'wb') as f:
                pickle.dump({
                    'data': self.data,
                    'timestamps': self.timestamps
                }, f)
        except IOError as e:
            raise DatabaseError(f"Failed to save to file: {str(e)}")
    
    def read(self, key: str, default: Any = None) -> Any:
        """Read a value from the database.

        Args:
            key (str): The key to look up.
            default (Any): The value to return if key is not found.

        Returns:
            Any: The value associated with the key or the default value.
        """
        return self.data.get(key, default)
    
    def write(self, key: str, value: Any, commit: bool = None) -> bool:
        """Write a value to the database.

        Args:
            key (str): The key under which to store the value.
            value (Any): The value to store.
            commit (bool): Whether to save changes to disk. If None, uses auto_commit setting.

        Returns:
            bool: True if write was successful.

        Raises:
            DatabaseError: If there's an error writing to the database.
        """
        try:
            self.data[key] = value
            self.timestamps[key] = datetime.now().isoformat()
            if commit or (commit is None and self.auto_commit):
                self._save_to_file()
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to write to Pickle database: {str(e)}")
    
    def keys(self, pattern: str = None) -> List[str]:
        """Get all keys in the database, optionally filtered by a pattern.

        Args:
            pattern (str): Optional pattern to filter keys.

        Returns:
            List[str]: List of matching keys.
        """
        if pattern:
            return [k for k in self.data.keys() if pattern in k]
        return list(self.data.keys())
    
    def delete_key(self, key: str, commit: bool = None) -> bool:
        """Delete a key from the database.

        Args:
            key (str): The key to delete.
            commit (bool): Whether to save changes to disk. If None, uses auto_commit setting.

        Returns:
            bool: True if deletion was successful.

        Raises:
            DatabaseError: If there's an error deleting the key.
        """
        try:
            if key in self.data:
                del self.data[key]
                if key in self.timestamps:
                    del self.timestamps[key]
                if commit or (commit is None and self.auto_commit):
                    self._save_to_file()
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to delete key: {str(e)}")
    
    def delete_database(self, commit: bool = None) -> bool:
        """Clear all data from the database.

        Args:
            commit (bool): Whether to save changes to disk. If None, uses auto_commit setting.

        Returns:
            bool: True if database was cleared successfully.

        Raises:
            DatabaseError: If there's an error clearing the database.
        """
        try:
            self.data.clear()
            self.timestamps.clear()
            if commit or (commit is None and self.auto_commit):
                self._save_to_file()
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to delete database: {str(e)}")
    
    def close(self) -> None:
        """Close the database and save if auto_commit is enabled."""
        if self.auto_commit:
            self._save_to_file()
    
    def remove_database(self) -> bool:
        """Remove the database file from disk.

        Returns:
            bool: True if file was removed successfully.

        Raises:
            DatabaseError: If there's an error removing the file.
        """
        try:
            if os.path.exists(self.name):
                os.remove(self.name)
            return True
        except OSError as e:
            raise DatabaseError(f"Failed to remove database file: {str(e)}")
    
    def get_size(self) -> int:
        """Get the number of keys in the database.

        Returns:
            int: Number of keys in the database.
        """
        return len(self.data)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in the database.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self.data