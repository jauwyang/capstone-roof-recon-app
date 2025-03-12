import sqlite3
from datetime import datetime

# DB_FILE = "images.db"
DB_FILE = "roof_inspection.db"

def add_images_to_set(image_set_id, dir_path, image_filenames):
    """Insert images into the database, linking them to an image set."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for filename in image_filenames:
        cursor.execute("""
            INSERT INTO images (image_set_id, filename, dir_path, damage_status, last_updated) 
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(image_set_id, filename) DO NOTHING
        """, (image_set_id, filename, dir_path, 0, datetime.now()))

    conn.commit()
    conn.close()


def add_image_set(set_name, dir_path):
    """Store a new image set if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if the directory is already stored
    cursor.execute("SELECT id FROM image_sets WHERE dir_path = ?", (dir_path,))
    result = cursor.fetchone()

    if result:
        print(f"Selected image set directory '{dir_path}' already exists.")
        conn.close()
        return result[0]  # Return existing set ID

    # Insert new image set
    cursor.execute("INSERT INTO image_sets (set_name, dir_path) VALUES (?, ?)", (set_name, dir_path))
    conn.commit()

    image_set_id = cursor.lastrowid  # Get the new set ID
    conn.close()
    return image_set_id


def get_all_image_sets():
    """Retrieve all image sets with their names, directory paths, and creation timestamps."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, set_name, dir_path, created_at
        FROM image_sets
    """)

    sets = cursor.fetchall()  # Returns list of (id, set_name, dir_path, created_at)
    conn.close()
    return sets



def get_predictions_for_image(image_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT x, y, width, height, confidence, class, detection_id 
        FROM predictions WHERE image_id = ?
    """, (image_id,))
    results = cursor.fetchall()

    conn.close()
    return results


def update_image_with_predictions(image_id, predictions):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Mark image as damaged
    cursor.execute("""
        UPDATE images
        SET damage_status = 1, last_updated = ?
        WHERE id = ?
    """, (datetime.now(), image_id))

    # 2. Insert new predictions
    for pred in predictions:
        cursor.execute("""
            INSERT INTO predictions 
            (image_id, x, y, width, height, confidence, class, class_id, detection_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_id,
            pred["x"], pred["y"], pred["width"], pred["height"],
            pred["confidence"], pred["class"], pred["class_id"],
            pred["detection_id"]
        ))

    conn.commit()
    conn.close()


def get_all_images_from_set(image_set_id):
    """
    Retrieve all images from a specific image set, including their directory path.

    print(get_all_images_from_set(1))
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, dir_path, damage_status 
        FROM images 
        WHERE image_set_id = ?
    """, (image_set_id,))
    results = cursor.fetchall()  # Returns list of (id, filename, dir_path, damage_status)
    conn.close()

    return results


def get_no_damage_images_from_set(image_set_id):
    """
    Retrieve images with no detected damage from a specific image set, including their directory path.
    
    print(get_no_damage_images_from_set(1))
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, dir_path
        FROM images
        WHERE image_set_id = ? AND damage_status = 0
    """, (image_set_id,))
    results = cursor.fetchall()  # Returns list of (id, filename, dir_path)
    conn.close()

    return results


def get_damaged_images_from_set(image_set_id):
    """
    Retrieve only images with detected damage from a specific image set, including their directory path.
    
    print(get_damaged_images_from_set(1))
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, dir_path
        FROM images
        WHERE image_set_id = ? AND damage_status = 1
    """, (image_set_id,))
    results = cursor.fetchall()  # Returns list of (id, filename, dir_path)
    conn.close()

    return results
