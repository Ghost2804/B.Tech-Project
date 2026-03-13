
import sqlite3
import json
import hashlib
import os

class Cache:
    def __init__(self, db_path="cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def _generate_key(self, content_str):
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    def get(self, content_str, model_suffix=""):
        """
        Retrieve value from cache. 
        model_suffix allows separating keys for different models/purposes 
        (e.g. 'embedding', 'summary').
        """
        key = self._generate_key(content_str + model_suffix)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM cache WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def set(self, content_str, value, model_suffix=""):
        """
        Save value to cache.
        """
        key = self._generate_key(content_str + model_suffix)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)
            """, (key, json.dumps(value)))
            conn.commit()

# Singleton instance
cache_manager = Cache()
