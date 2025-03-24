import sqlite3


# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# Database setup function
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Function to add sample user
def add_sample_user():
    conn = get_db_connection()
    
    # Check if data already exists
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    if user_count == 0:
        # Add sample user
        conn.execute('''
            INSERT INTO users (phone_number, email)
            VALUES (?, ?)
        ''', ('0123456789', 'user@example.com'))
        
        conn.commit()
    
    conn.close()
