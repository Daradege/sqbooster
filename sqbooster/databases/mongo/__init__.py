"""
This module provides a MongoDB database interface for storing and retrieving data.
The MongoDatabase class provides methods to interact with a MongoDB database.
It allows reading, writing, and deleting key-value pairs, as well as retrieving all keys.
"""

from ...exceptions import ConnectionError,DatabaseError,KeyNotFoundError,SerializationError
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    
    class MongoDatabase:
        """A MongoDB database interface for storing and retrieving data.

        Args:
            name (str, optional): Name of the database. Defaults to "testdb".
            host (str, optional): MongoDB server host. Defaults to "localhost".
            port (int, optional): MongoDB server port. Defaults to 27017.
            collection (str, optional): Name of the collection. Defaults to "data".
            auto_commit (bool, optional): Whether to auto commit changes. Defaults to True.

        Raises:
            ConnectionError: If connection to MongoDB fails.
        """

        def __init__(self, name: str = "testdb", host: str = "localhost", port: int = 27017,
                     collection: str = "data", auto_commit: bool = True):
            """Initialize MongoDB connection"""
            self.name = name
            self.collection_name = collection
            self.auto_commit = auto_commit
            try:
                self.client = MongoClient(host, port)
                self.db = self.client[name]
                self.collection = self.db[collection]
            except PyMongoError as e:
                raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
        
        def read(self, key: str, default: Any = None) -> Any:
            """Read a value from the database.

            Args:
                key (str): The key to read.
                default (Any, optional): Default value if key not found. Defaults to None.

            Returns:
                Any: The value associated with the key.

            Raises:
                DatabaseError: If reading from MongoDB fails.
            """
            try:
                result = self.collection.find_one({"_id": key})
                return result["value"] if result else default
            except PyMongoError as e:
                raise DatabaseError(f"Failed to read from MongoDB: {str(e)}")
        
        def write(self, key: str, value: Any, commit: bool = None) -> bool:
            """Write a key-value pair to the database.

            Args:
                key (str): The key to write.
                value (Any): The value to store.
                commit (bool, optional): Whether to commit the change. Defaults to None.

            Returns:
                bool: True if write successful.

            Raises:
                DatabaseError: If writing to MongoDB fails.
            """
            try:
                doc = {
                    "_id": key,
                    "value": value,
                    "created_at": datetime.now().isoformat()
                }
                self.collection.replace_one({"_id": key}, doc, upsert=True)
                return True
            except PyMongoError as e:
                raise DatabaseError(f"Failed to write to MongoDB: {str(e)}")
        
        def keys(self, pattern: str = None) -> List[str]:
            """Get all keys in the database matching a pattern.

            Args:
                pattern (str, optional): Regex pattern to match keys. Defaults to None.

            Returns:
                List[str]: List of matching keys.

            Raises:
                DatabaseError: If fetching keys fails.
            """
            try:
                if pattern:
                    cursor = self.collection.find({"_id": {"$regex": pattern}}, {"_id": 1})
                else:
                    cursor = self.collection.find({}, {"_id": 1})
                return [doc["_id"] for doc in cursor]
            except PyMongoError as e:
                raise DatabaseError(f"Failed to fetch keys: {str(e)}")
        
        def delete_key(self, key: str, commit: bool = None) -> bool:
            """Delete a key from the database.

            Args:
                key (str): The key to delete.
                commit (bool, optional): Whether to commit the change. Defaults to None.

            Returns:
                bool: True if deletion successful.

            Raises:
                DatabaseError: If deleting key fails.
            """
            try:
                self.collection.delete_one({"_id": key})
                return True
            except PyMongoError as e:
                raise DatabaseError(f"Failed to delete key: {str(e)}")
        
        def delete_database(self, commit: bool = None) -> bool:
            """Delete all data from the database.

            Args:
                commit (bool, optional): Whether to commit the change. Defaults to None.

            Returns:
                bool: True if deletion successful.

            Raises:
                DatabaseError: If deleting database fails.
            """
            try:
                self.collection.delete_many({})
                return True
            except PyMongoError as e:
                raise DatabaseError(f"Failed to delete database: {str(e)}")
        
        def close(self) -> None:
            """Close the database connection.

            Raises:
                ConnectionError: If closing connection fails.
            """
            try:
                self.client.close()
            except PyMongoError as e:
                raise ConnectionError(f"Failed to close MongoDB connection: {str(e)}")
        
        def get_size(self) -> int:
            """Get the number of documents in the database.

            Returns:
                int: Number of documents.

            Raises:
                DatabaseError: If getting size fails.
            """
            try:
                return self.collection.count_documents({})
            except PyMongoError as e:
                raise DatabaseError(f"Failed to get database size: {str(e)}")
        
        def exists(self, key: str) -> bool:
            """Check if a key exists in the database.

            Args:
                key (str): The key to check.

            Returns:
                bool: True if key exists, False otherwise.

            Raises:
                DatabaseError: If checking existence fails.
            """
            try:
                return bool(self.collection.find_one({"_id": key}))
            except PyMongoError as e:
                raise DatabaseError(f"Failed to check key existence: {str(e)}")

except ImportError:
    class MongoDatabase:
        """Fallback class when PyMongo is not installed."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyMongo library not installed. Install with: pip install pymongo")