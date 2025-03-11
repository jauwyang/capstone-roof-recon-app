from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
import os

from imageSetDB import *


CONFIDENCE_THRESH = 0.25

class RoofDetectionModel:
    def __init__(self, use_local_model = False):
        self.use_local_model = use_local_model
        
        # Initialize the model
        if self.use_local_model:
            self.model = YOLO("best.pt")  # Load local YOLO model
        else:
            self.CLIENT = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key="eyy15gP8oZtUIzN3KfRC"  # Replace with your actual API key
            )

    def predict(self, dir_path, image_names):
        for image_name in image_names:
            img_path = os.path.join(dir_path, image_name)
            
            if self.use_local_model:
                ...
            else:
                # Roboflow API inference
                result = self.CLIENT.infer(img_path, model_id="roof-damage-detection-7zpct-xitjh/2")
                predictions = result['predictions']
                filtered_predictions = []
                
                for p in predictions:
                    if p['confidence'] > CONFIDENCE_THRESH:
                        filtered_predictions.append({
                            "x": p["x"],
                            "y": p["y"],
                            "width": p["width"],
                            "height": p["height"],
                            "confidence": p["confidence"],
                            "class": p["class"],
                            "class_id": p["class_id"],
                            "detection_id": p["detection_id"]
                        })
            
            if filtered_predictions:
                update_image_with_predictions(dir_path, image_name, filtered_predictions)