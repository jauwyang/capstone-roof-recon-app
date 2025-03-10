import cv2
import os
import numpy as np


def draw_bounding_boxes(image, detected_defects):
    h, w, _ = image.shape
    for defect in detected_defects:
        x, y = np.random.randint(0, w - 50), np.random.randint(0, h - 50)
        color = (0, 255, 0) if defect == "Degranulation" else (0, 0, 255)
        cv2.rectangle(image, (x, y), (x + 100, y + 50), color, 2)
        cv2.putText(image, defect, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return image


def save_annotated_image(original_path, image):
    save_dir = "reports/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, os.path.basename(original_path))
    cv2.imwrite(save_path, image)
