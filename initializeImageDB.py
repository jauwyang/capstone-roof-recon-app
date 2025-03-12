import sqlite3
import os

DB_FILE = "roof_inspection.db"  # Change this to your preferred database name

def initialize_database(reset=False):
    """
    Initializes the database with required tables.
    If reset=True, it will DROP existing tables and create fresh ones.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if reset:
        # Drop existing tables
        cursor.executescript("""
            DROP TABLE IF EXISTS predictions;
            DROP TABLE IF EXISTS images;
            DROP TABLE IF EXISTS image_sets;
        """)

    # Create image_sets table (Stores directories)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            set_name TEXT UNIQUE NOT NULL,
            dir_path TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create images table (Stores image metadata)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_set_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        dir_path TEXT NOT NULL,
        damage_status INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (image_set_id) REFERENCES image_sets(id) ON DELETE CASCADE,
        UNIQUE (filename, image_set_id)  -- ✅ Ensure unique filenames per image set
    )
    """)

    # Create predictions table (Stores model detections)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            confidence REAL NOT NULL,
            class TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            detection_id TEXT UNIQUE NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!" if not reset else "Database reset and re-initialized!")

# Example Usage
initialize_database(reset=True)  # Pass reset=True to wipe everything


# import sqlite3

# DB_FILE = "images.db"

# def initialize_database():
#     """Create the database and tables if they do not exist."""
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()

#     # Create images table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS images (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             dir_path TEXT NOT NULL,
#             filename TEXT NOT NULL UNIQUE,
#             damage_status INTEGER DEFAULT 0, -- 0 = no damage, 1 = damaged
#             last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     # Create predictions table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS predictions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             image_id INTEGER NOT NULL, -- Links to images table
#             x INTEGER, y INTEGER, width INTEGER, height INTEGER,
#             confidence REAL, class TEXT, class_id INTEGER,
#             detection_id TEXT UNIQUE,
#             FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
#         )
#     """)

#     conn.commit()
#     conn.close()
#     print("✅ Database initialized successfully.")


# def reset_database():
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
    
#     cursor.execute("DELETE FROM images")  # Delete all data
#     cursor.execute("DELETE FROM sqlite_sequence WHERE name='images'")  # Reset auto-increment
#     conn.commit()
#     conn.close()

# def reset_predictions():
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
    
#     cursor.execute("DELETE FROM predictions")  # Delete all records
#     cursor.execute("DELETE FROM sqlite_sequence WHERE name='predictions'")  # Reset auto-increment
    
#     conn.commit()
#     conn.close()
#     print("✅ Predictions table reset successfully.")





# # Run the function to initialize the database
# # initialize_database()
# reset_database()
# reset_predictions()