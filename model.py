# from PyQt6.QtCore import QThread, pyqtSignal
# from ultralytics import YOLO
# from inference_sdk import InferenceHTTPClient
# import os

# from imageSetDB import update_image_with_predictions  # Ensure correct import

# CONFIDENCE_THRESH = 0.25


# class RoofDetectionWorker(QThread):
#     progress_updated = pyqtSignal(int)  # Signal to update progress bar
#     prediction_done = pyqtSignal(str)   # Signal when a prediction is completed

#     def __init__(self, model, dir_path, image_names):
#         super().__init__()
#         self.model = model
#         self.dir_path = dir_path
#         self.image_names = image_names

#     def run(self):
#         total_images = len(self.image_names)

#         for i, image_name in enumerate(self.image_names):
#             img_path = os.path.join(self.dir_path, image_name)
#             filtered_predictions = []

#             if self.model.use_local_model:
#                 # Local YOLO model inference
#                 results = self.model.model.predict(img_path)
#                 for result in results:
#                     for box in result.boxes:
#                         conf = box.conf.item()
#                         if conf > CONFIDENCE_THRESH:
#                             x, y, w, h = box.xywhn.tolist()[0]
#                             filtered_predictions.append({
#                                 "x": x,
#                                 "y": y,
#                                 "width": w,
#                                 "height": h,
#                                 "confidence": conf,
#                                 "class": result.names[box.cls.item()],
#                                 "class_id": int(box.cls.item())
#                             })
#             else:
#                 # Roboflow API inference
#                 result = self.model.CLIENT.infer(img_path, model_id="roof-damage-detection-7zpct-xitjh/2")
#                 predictions = result.get('predictions', [])

#                 for p in predictions:
#                     if p['confidence'] > CONFIDENCE_THRESH:
#                         filtered_predictions.append({
#                             "x": p["x"],
#                             "y": p["y"],
#                             "width": p["width"],
#                             "height": p["height"],
#                             "confidence": p["confidence"],
#                             "class": p["class"],
#                             "class_id": p["class_id"],
#                             "detection_id": p.get("detection_id", None)
#                         })

#                 self.progress_updated.emit(i + 1)

#             # Save results
#             if filtered_predictions:
#                 update_image_with_predictions(self.dir_path, image_name, filtered_predictions)

#             # Emit progress update (convert to percentage)
#             progress_percent = int(((i + 1) / total_images) * 100)
#             self.progress_updated.emit(progress_percent)
#             self.prediction_done.emit(image_name)


# class RoofDetectionModel:
#     def __init__(self, use_local_model=False):
#         self.use_local_model = use_local_model

#         # Initialize the model
#         if self.use_local_model:
#             self.model = YOLO("best.pt")  # Load local YOLO model
#         else:
#             self.CLIENT = InferenceHTTPClient(
#                 api_url="https://detect.roboflow.com",
#                 api_key="eyy15gP8oZtUIzN3KfRC"  # Replace with your actual API key
#             )

#     def predict(self, dir_path, image_names, predictionProgressBar):
#         self.worker = RoofDetectionWorker(self, dir_path, image_names)
#         self.worker.progress_updated.connect(predictionProgressBar.setValue)  # Connect to UI
#         self.worker.start()  # Start in a separate thread

from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
from PyQt6.QtWidgets import QProgressBar
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

    def predict(self, dir_path, image_names, image_ids, predictionProgressBar: QProgressBar):
        i = 0
        for image_name in image_names:
            predictionProgressBar.setValue(i+1)
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
                update_image_with_predictions(image_ids[i], filtered_predictions)
            i+=1