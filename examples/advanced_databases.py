"""
Advanced Databases Example - sqbooster

This example demonstrates usage of Redis, MongoDB, and PostgreSQL databases
with proper error handling for optional dependencies.
"""

def test_redis():
    """Test Redis database functionality."""
    try:
        from sqbooster.databases import RedisDatabase
        
        print("--- Redis Database ---")
        db = RedisDatabase()
        
        # Test data
        test_data = {
            "session:123": {"user_id": 456, "login_time": "2024-01-01T10:00:00"},
            "cache:weather": {"city": "London", "temp": 15, "humidity": 80},
            "config:app": {"theme": "dark", "language": "en", "notifications": True}
        }
        
        # Write and read data
        for key, value in test_data.items():
            db.write(key, value)
            retrieved = db.read(key)
            print(f"Redis - {key}: {retrieved}")
        
        # Test expiration (Redis-specific feature)
        db.write("temp:data", {"message": "This will expire"})
        print(f"Temporary data exists: {db.exists('temp:data')}")
        
        print("Redis test completed successfully!\n")
        
    except ImportError:
        print("Redis not available. Install with: pip install redis\n")
    except Exception as e:
        print(f"Redis connection failed: {e}\n")

def test_mongodb():
    """Test MongoDB database functionality."""
    try:
        from sqbooster.databases import MongoDatabase
        
        print("--- MongoDB Database ---")
        db = MongoDatabase()
        
        # Test data with complex nested structures
        test_data = {
            "product:1": {
                "name": "Laptop",
                "specs": {"cpu": "Intel i7", "ram": "16GB", "storage": "512GB SSD"},
                "price": 999.99,
                "tags": ["electronics", "computers", "portable"]
            },
            "order:1001": {
                "customer": "john.doe@example.com",
                "items": [
                    {"product_id": "product:1", "quantity": 1, "price": 999.99}
                ],
                "total": 999.99,
                "status": "pending"
            }
        }
        
        # Write and read data
        for key, value in test_data.items():
            db.write(key, value)
            retrieved = db.read(key)
            print(f"MongoDB - {key}: {retrieved}")
        
        print("MongoDB test completed successfully!\n")
        
    except ImportError:
        print("MongoDB not available. Install with: pip install pymongo\n")
    except Exception as e:
        print(f"MongoDB connection failed: {e}\n")

def test_postgresql():
    """Test PostgreSQL database functionality."""
    try:
        from sqbooster.databases import PostgreSQLDatabase
        
        print("--- PostgreSQL Database ---")
        db = PostgreSQLDatabase()
        
        # Test data with various data types
        test_data = {
            "analytics:daily": {
                "date": "2024-01-01",
                "visitors": 1250,
                "page_views": 3500,
                "bounce_rate": 0.35,
                "top_pages": ["/home", "/products", "/about"]
            },
            "user:profile:123": {
                "username": "alice_smith",
                "email": "alice@example.com",
                "preferences": {
                    "theme": "light",
                    "notifications": {"email": True, "push": False}
                },
                "last_login": "2024-01-01T15:30:00"
            }
        }
        
        # Write and read data
        for key, value in test_data.items():
            db.write(key, value)
            retrieved = db.read(key)
            print(f"PostgreSQL - {key}: {retrieved}")
        
        print("PostgreSQL test completed successfully!\n")
        
    except ImportError:
        print("PostgreSQL not available. Install with: pip install psycopg2-binary\n")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}\n")

def main():
    print("=== Advanced Databases Example ===\n")
    print("Testing optional database integrations...\n")
    
    test_redis()
    test_mongodb()
    test_postgresql()
    
    print("Note: Make sure the respective database servers are running")
    print("and accessible with default connection parameters.")

if __name__ == "__main__":
    main()
