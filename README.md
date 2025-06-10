# sqbooster

[![PyPI version](https://badge.fury.io/py/sqbooster.svg)](https://badge.fury.io/py/sqbooster)
[![Python Version](https://img.shields.io/pypi/pyversions/sqbooster.svg)](https://pypi.org/project/sqbooster/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library that provides a flexible and easy-to-use interface for working with various databases, including SQLite, JSON, Pickle, Redis, MongoDB, and PostgreSQL.

## Features

- **Multiple Database Support:** Work with SQLite, JSON files, Pickle files, Redis, MongoDB, and PostgreSQL
- **Consistent API:** Same interface across all database types
- **Automatic Serialization:** Built-in JSON serialization/deserialization for complex data types
- **Lightweight:** Minimal dependencies for core functionality
- **Optional Integrations:** Support for popular databases like Redis and MongoDB
- **Type Safety:** Python type hints for better IDE support
- **Error Handling:** Robust error handling and informative exceptions

## Installation

```bash
pip install sqbooster
```

## Quick Start

```python
from sqbooster.databases import SQLiteDatabase, JSONFileDatabase, PickleFileDatabase

# SQLite Example
db_sqlite = SQLiteDatabase("test.db")
db_sqlite.write("key1", {"name": "test", "value": 123})
print("SQLite:", db_sqlite.read("key1"))

# JSON File Example
db_json = JSONFileDatabase("test.json")
db_json.write("key1", {"name": "test", "value": 123})
print("JSON File:", db_json.read("key1"))

# Pickle File Example
db_pickle = PickleFileDatabase("test.pkl")
db_pickle.write("key1", {"name": "test", "value": 123})
print("Pickle File:", db_pickle.read("key1"))
```

## Advanced Usage

### Redis Integration

```python
from sqbooster.databases import RedisDatabase

try:
    db_redis = RedisDatabase()
    db_redis.write("key1", {"name": "test", "value": 123})
    print("Redis:", db_redis.read("key1"))
except ImportError:
    print("Redis not available")
```

### MongoDB Integration

```python
from sqbooster.databases import MongoDatabase

try:
    db_mongo = MongoDatabase()
    db_mongo.write("key1", {"name": "test", "value": 123})
    print("MongoDB:", db_mongo.read("key1"))
except ImportError:
    print("MongoDB not available")
```

### PostgreSQL Integration

```python
from sqbooster.databases import PostgreSQLDatabase

try:
    db_postgres = PostgreSQLDatabase()
    db_postgres.write("key1", {"name": "test", "value": 123})
    print("PostgreSQL:", db_postgres.read("key1"))
except ImportError:
    print("PostgreSQL not available")
```

## API Reference

All database classes implement the following core methods:

- `write(key, value)`: Store a value with the given key
- `read(key)`: Retrieve a value by key
- `delete(key)`: Remove a key-value pair
- `exists(key)`: Check if a key exists
- `clear()`: Remove all key-value pairs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Ali Safamanesh (darg.q.a.a@gmail.com)
