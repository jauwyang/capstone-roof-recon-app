import cv2
import os

def save_image(image, save_dir="assets/"):
    """Saves processed image and returns path."""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, "processed_image.jpg")
    cv2.imwrite(save_path, image)
    return save_path