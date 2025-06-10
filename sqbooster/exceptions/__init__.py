"""
This module defines exceptions used in the sqbooster package.
"""

class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class KeyNotFoundError(DatabaseError):
    """Raised when a key is not found in the database"""
    pass

class ConnectionError(DatabaseError):
    """Raised when there's an issue with the database connection"""
    pass

class SerializationError(DatabaseError):
    """Raised when there's an issue with JSON serialization/deserialization"""
    pass