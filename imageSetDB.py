import sqlite3
from datetime import datetime

DB_FILE = "images.db"

def add_images_without_damage(dir_path, image_filenames):
    """
    Insert images into the database, assuming no damage initially.

    # Example usage:
    image_files = ["roof1.jpg", "roof2.jpg", "roof3.jpg"]
    add_images_without_damage("/home/user/roof_images/", image_files)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for filename in image_filenames:
        cursor.execute("""
            INSERT INTO images (dir_path, filename, damage_status, last_updated) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(filename) DO NOTHING
        """, (dir_path, filename, 0, datetime.now()))  

    conn.commit()
    conn.close()


def update_image_with_predictions(dir_path, filename, predictions):
    """
    Update an image's damage status and store bounding boxes from model predictions.

    # Example usage:
    image_predictions = {
        "predictions": [
            {
                "x": 661, "y": 294, "width": 38, "height": 34,
                "confidence": 0.54, "class": "Puncture",
                "class_id": 4, "detection_id": "b05ade64-c7f5-426b-9ec1-6c05f63dd0af"
            }
        ]
    }

    update_image_with_predictions("/home/user/roof_images/", "roof1.jpg", image_predictions["predictions"])

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Get image ID based on dir_path & filename
    cursor.execute("SELECT id FROM images WHERE dir_path = ? AND filename = ?", (dir_path, filename))
    result = cursor.fetchone()
    if not result:
        print(f"Image {filename} not found in {dir_path}.")
        conn.close()
        return
    
    image_id = result[0]

    # 2. Mark image as damaged
    cursor.execute("""
        UPDATE images
        SET damage_status = 1, last_updated = ?
        WHERE id = ?
    """, (datetime.now(), image_id))

    # 3. Insert new predictions
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


def get_all_images_from_dir(dir_path):
    """
    Retrieve all images from a specific directory.

    print(get_all_images_from_dir("/home/user/roof_images/"))

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, damage_status FROM images WHERE dir_path = ?", (dir_path,))
    results = cursor.fetchall()  # Returns list of (id, filename, damage_status)
    conn.close()

    return results


def get_damaged_images_from_dir(dir_path):
    """
    Retrieve only images with detected damage from a specific directory.
    
    print(get_damaged_images_from_dir("/home/user/roof_images/"))

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename
        FROM images
        WHERE dir_path = ? AND damage_status = 1
    """, (dir_path,))
    results = cursor.fetchall()  # Returns list of (id, filename)
    conn.close()

    return results


def get_no_damage_images_from_dir(dir_path):
    """Retrieve images with no detected damage from a specific directory."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename
        FROM images
        WHERE dir_path = ? AND damage_status = 0
    """, (dir_path,))
    results = cursor.fetchall()  # Returns list of (id, filename)
    conn.close()

    return results


def get_predictions_for_image(dir_path, filename):
    """Retrieve all damage predictions for a specific image."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM images WHERE dir_path = ? AND filename = ?
    """, (dir_path, filename))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return []
    
    image_id = result[0]


    cursor.execute("""
        SELECT x, y, width, height, confidence, class, detection_id 
        FROM predictions WHERE image_id = ?
    """, (image_id,))
    results = cursor.fetchall()

    conn.close()

    return results