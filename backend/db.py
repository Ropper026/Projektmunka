import sqlite3

DB_NAME = "properties.db"
USER_DB_NAME = "users.db"

def create_database():
    """Create the database and the properties table if it doesn't exist."""
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            location TEXT NOT NULL,
            rooms INTEGER NOT NULL,
            area REAL NOT NULL,
            image_path TEXT,
            username TEXT NOT NULL  -- Add username column
        )
    """)
    cursor.execute("PRAGMA table_info(properties)")
    columns = [column[1] for column in cursor.fetchall()]
    if "username" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN username TEXT DEFAULT 'unknown' NOT NULL")
    connection.commit()
    connection.close()

def create_user_database():
    """Create the user database and the users table if it doesn't exist."""
    connection = sqlite3.connect(USER_DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def get_db_connection():
    """Get a connection to the database."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row 
    return connection

def get_user_db_connection():
    """Get a connection to the user database."""
    connection = sqlite3.connect(USER_DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection