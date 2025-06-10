"""
sqbooster - A lightweight Python library for SQLite-based key-value storage.

sqbooster provides a simple and efficient way to store and retrieve key-value
pairs using SQLite as the backend database. It's designed for small to medium
projects that need persistent storage without the complexity of full-featured
database solutions.

Key Features:
- Simple, intuitive API for key-value operations
- Automatic JSON serialization/deserialization for complex data types
- SQLite backend for reliability and portability
- Lightweight with minimal dependencies
- Perfect for single-file projects and rapid prototyping

Example Usage:
    from sqbooster.databases import SQLiteDatabase

    # SQLite
    db_sqlite = SQLiteDatabase("test.db")
    db_sqlite.write("key1", {"name": "test", "value": 123})
    print("SQLite:", db_sqlite.read("key1"))
    
    # JSON File
    db_json = JSONFileDatabase("test.json")
    db_json.write("key1", {"name": "test", "value": 123})
    print("JSON File:", db_json.read("key1"))
    
    # Pickle File
    db_pickle = PickleFileDatabase("test.pkl")
    db_pickle.write("key1", {"name": "test", "value": 123})
    print("Pickle File:", db_pickle.read("key1"))
    
    # Redis (if available)
    try:
        db_redis = RedisDatabase()
        db_redis.write("key1", {"name": "test", "value": 123})
        print("Redis:", db_redis.read("key1"))
    except ImportError:
        print("Redis not available")
    
    # MongoDB (if available)
    try:
        db_mongo = MongoDatabase()
        db_mongo.write("key1", {"name": "test", "value": 123})
        print("MongoDB:", db_mongo.read("key1"))
    except ImportError:
        print("MongoDB not available")
    
    # PostgreSQL (if available)
    try:
        db_postgres = PostgreSQLDatabase()
        db_postgres.write("key1", {"name": "test", "value": 123})
        print("PostgreSQL:", db_postgres.read("key1"))
    except ImportError:
        print("PostgreSQL not available")

This library is ideal for applications that need simple persistent storage,
configuration management, caching, or any scenario where you want the
convenience of a dictionary with database persistence.
"""
