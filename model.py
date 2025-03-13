from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
from PyQt6.QtWidgets import QProgressBar, QMessageBox
import os
import requests
import urllib3


from imageSetDB import *


# CONFIDENCE_THRESH = 0.25
CONFIDENCE_THRESH = 0.11

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

    def predict(self, dir_path, image_names, image_ids, predictionProgressBar: QProgressBar):
        i = 0
        for image_name in image_names:
            predictionProgressBar.setValue(i+1)
            img_path = os.path.join(dir_path, image_name)
            
            if self.use_local_model:
                ...
            else:
                # Roboflow API inference
                try:
                    result = self.CLIENT.infer(img_path, model_id="roof-damage-detection-7zpct-xitjh/2")
                except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError):
                    self.showErrorPopup("Network Error", "Unable to connect to the AI model API. Please check your internet connection and try again.")
                except Exception as e:
                    self.showErrorPopup("Unexpected Error", f"An error occurred: {str(e)}")

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
                update_image_with_predictions(image_ids[i], filtered_predictions)
            i+=1

    def showErrorPopup(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()