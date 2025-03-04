import cv2
import numpy as np
import os
from core.image_utils import save_image

class AIModel:
    def __init__(self):
        # Load model (Replace with your AI model)
        print("Model loaded.")

    def run_inference(self, image_path):
        image = cv2.imread(image_path)
        processed_image = self.process_image(image)  # Apply transformation
        output_path = save_image(processed_image)
        return output_path

    def process_image(self, image):
        """Simple inversion (replace with AI processing)"""
        return 255 - image  # Invert colors