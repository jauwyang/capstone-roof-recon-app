import sqlite3

DB_FILE = "images.db"

def initialize_database():
    """Create the database and tables if they do not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dir_path TEXT NOT NULL,
            filename TEXT NOT NULL UNIQUE,
            damage_status INTEGER DEFAULT 0, -- 0 = no damage, 1 = damaged
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL, -- Links to images table
            x INTEGER, y INTEGER, width INTEGER, height INTEGER,
            confidence REAL, class TEXT, class_id INTEGER,
            detection_id TEXT UNIQUE,
            FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


def reset_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM images")  # Delete all data
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='images'")  # Reset auto-increment
    conn.commit()
    conn.close()

def reset_predictions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM predictions")  # Delete all records
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='predictions'")  # Reset auto-increment
    
    conn.commit()
    conn.close()
    print("✅ Predictions table reset successfully.")





# Run the function to initialize the database
# initialize_database()
reset_database()
reset_predictions()