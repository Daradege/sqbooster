import sqlite3
import json

class db:
    def __init__(self,name):
        self.name = name
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS key_value_store
                        (key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()
        conn.close()
    def read_database(self):
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM key_value_store")
        rows = cursor.fetchall()
        conn.close()
        return {key: json.loads(value) for key, value in rows}
    def write_database(self,data_dict):
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()
        for key, value in data_dict.items():
            cursor.execute("INSERT OR REPLACE INTO key_value_store (key, value) VALUES (?, ?)",
                        (key, json.dumps(value, default=list)))
        conn.commit()
        conn.close()
    def read_key(self,key:str,default):
        db = self.read_database()
        if key in db.keys():
            return db[key]
        else:
            return default
    
    def write_key(self,key:str,value):
        db = self.read_database()
        db[key] = value
        self.write_database(db)
    
    def keys(self):
        db = self.read_database()
        return db.keys()
