"""
Database backends for sqbooster.

This module provides database backend implementations for the sqbooster
key-value store library. Currently supports SQLite as the primary backend
for persistent storage of key-value pairs with automatic JSON serialization.

The database backends handle the low-level storage operations while providing
a consistent interface for the higher-level sqbooster API.
"""