import cv2
import numpy as np
import os
from core.image_utils import draw_bounding_boxes, save_annotated_image

# Simulated AI Model (Replace with actual AI inference)
class RoofInspectionModel:
    def __init__(self):
        self.defect_classes = {
            "Degranulation": "Aging or shingle uplifting.",
            "Cracking": "Caused by thermal stress and aging.",
            "Moss Growth": "Indicates trapped moisture, reducing roof lifespan."
        }

    def run_inference_on_directory(self, image_dir):
        results = {}
        for img_name in os.listdir(image_dir):
            img_path = os.path.join(image_dir, img_name)
            if img_path.lower().endswith(("png", "jpg", "jpeg")):
                detected_defects = self.simulate_model(img_path)
                results[img_name] = detected_defects
                self.annotate_and_save(img_path, detected_defects)
        return results

    def simulate_model(self, image_path):
        # Simulating detections (Replace with actual model inference)
        return np.random.choice(list(self.defect_classes.keys()), size=np.random.randint(1, 3), replace=False).tolist()

    def annotate_and_save(self, image_path, detected_defects):
        image = cv2.imread(image_path)
        annotated_image = draw_bounding_boxes(image, detected_defects)
        save_annotated_image(image_path, annotated_image)

    def get_defect_details(self, image_name):
        return "\n".join([f"{d}: {self.defect_classes[d]}" for d in np.random.choice(list(self.defect_classes.keys()), 2)])