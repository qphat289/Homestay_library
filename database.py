import sqlite3
from sqlite3 import Error
import os
from contextlib import contextmanager
from queue import Queue
import threading

# Connection pool settings
MAX_CONNECTIONS = 10
POOL_TIMEOUT = 30  # seconds

class DatabasePool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabasePool, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        self.pool = Queue(maxsize=MAX_CONNECTIONS)
        self.db_path = 'database.db'
        
        # Create initial connections
        for _ in range(MAX_CONNECTIONS):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
    
    def _create_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except Error as e:
            print(f"Error creating database connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self.pool.get(timeout=POOL_TIMEOUT)
            yield conn
        except Exception as e:
            print(f"Error getting connection from pool: {e}")
            if conn:
                self.pool.put(conn)
            raise
        finally:
            if conn:
                self.pool.put(conn)
    
    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

# Initialize database pool
db_pool = DatabasePool()

def init_db():
    """Initialize the database with required tables"""
    with db_pool.get_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()

def get_db():
    """Get a database connection from the pool"""
    return db_pool.get_connection()

def close_db():
    """Close all database connections"""
    db_pool.close_all()

if __name__ == '__main__':
    init_db()
