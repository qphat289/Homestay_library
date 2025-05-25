import sqlite3
from database import get_db_connection

def migrate_data():
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect('database.db')
        sqlite_conn.row_factory = sqlite3.Row
        
        # Connect to PostgreSQL
        pg_conn = get_db_connection()
        pg_cur = pg_conn.cursor()
        
        # Migrate users
        sqlite_users = sqlite_conn.execute('SELECT * FROM users').fetchall()
        for user in sqlite_users:
            pg_cur.execute(
                'INSERT INTO users (phone_number, email) VALUES (%s, %s)',
                (user['phone_number'], user['email'])
            )
        
        pg_conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
    finally:
        # Close connections
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_cur' in locals():
            pg_cur.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == '__main__':
    migrate_data()
