import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Create connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # minconn
    10, # maxconn
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    port=os.getenv('POSTGRES_PORT', '5432'),
    sslmode='require'
)

def get_db_connection():
    """Get database connection from pool"""
    conn = connection_pool.getconn()
    conn.cursor_factory = RealDictCursor
    return conn

def release_db_connection(conn):
    """Release connection back to pool"""
    connection_pool.putconn(conn)

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        # Add indexes for frequently queried columns
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        
        conn.commit()
    finally:
        cur.close()
        release_db_connection(conn)

if __name__ == '__main__':
    init_db()
