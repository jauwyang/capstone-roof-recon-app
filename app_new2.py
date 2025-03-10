import sys
import os
import sqlite3
from datetime import datetime
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QScrollArea, QHBoxLayout, QStackedWidget
)
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient

CONFIDENCE_THRESH = 0.25

class RoofInspectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roof Recon")
        self.setGeometry(100, 100, 1200, 800)
        
        self.use_local_model = False
        
        # Initialize the model
        if self.use_local_model:
            self.model = YOLO("best.pt")  # Load local YOLO model
        else:
            self.CLIENT = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key="eyy15gP8oZtUIzN3KfRC"  # Replace with your actual API key
            )
        
        
        self.init_db()
        
        self.main_layout = QVBoxLayout()
        self.tabs_layout = QHBoxLayout()
        self.stack = QStackedWidget()
        
        self.detect_tab = DetectTab(self)
        self.history_tab = HistoryTab(self)
        self.user_guide_tab = UserGuideTab()
        
        self.stack.addWidget(self.detect_tab)
        self.stack.addWidget(self.history_tab)
        self.stack.addWidget(self.user_guide_tab)
        
        self.detect_button = QPushButton("Detect")
        self.history_button = QPushButton("History")
        self.user_guide_button = QPushButton("User Guide")
        
        for i, btn in enumerate([self.detect_button, self.history_button, self.user_guide_button]):
            btn.setStyleSheet("background-color: white; padding: 10px; border: none; font-size: 14px; font-weight: bold;")
            btn.clicked.connect(lambda _, x=i: self.switch_tab(x))
            self.tabs_layout.addWidget(btn)
        
        self.main_layout.addLayout(self.tabs_layout)
        self.main_layout.addWidget(self.stack)
        
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        
        self.switch_tab(0)
    
    def init_db(self):
        self.conn = sqlite3.connect("inspection_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                            (id INTEGER PRIMARY KEY, directory TEXT, timestamp TEXT)''')
        self.conn.commit()
    
    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
    
    def add_to_history(self, directory):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO history (directory, timestamp) VALUES (?, ?)", (directory, timestamp))
        self.conn.commit()
        self.history_tab.load_history()


class DetectTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.defect_images = []
        
        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Upload Image Set")
        self.predict_btn = QPushButton("Predict Image Set")
        self.toggle_btn = QPushButton("Toggle Detections")
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.predict_btn)
        button_layout.addWidget(self.toggle_btn)
        layout.addLayout(button_layout)
        
        self.image_display = QLabel("No image loaded")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_display)
        
        self.detection_info = QLabel("No Image Loaded")
        self.detection_info.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.detection_info)
        
        self.scroll_area = QScrollArea()
        self.image_list_widget = QWidget()
        self.image_list_layout = QHBoxLayout()
        self.image_list_widget.setLayout(self.image_list_layout)
        self.scroll_area.setWidget(self.image_list_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
        self.upload_btn.clicked.connect(self.load_directory)
        self.predict_btn.clicked.connect(self.run_model_on_directory)
        self.toggle_btn.clicked.connect(self.toggle_detections)
    
    def load_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.run_model_on_directory(dir_path)
            self.parent.add_to_history(dir_path)
    
    def run_model_on_directory(self, dir_path):
        self.defect_images.clear()
        detected_classes = set()
        
        for file in os.listdir(dir_path):
            if file.endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(dir_path, file)
                
                if self.parent.use_local_model:
                    results = self.parent.model(img_path)
                    if len(results[0].boxes) > 0:
                        self.defect_images.append(img_path)
                else:
                    # Roboflow API inference
                    result = self.parent.CLIENT.infer(img_path, model_id="roof-damage-detection-7zpct-xitjh/2")
                    predictions = result['predictions']
                    
                    for p in predictions:
                        if p['confidence'] > CONFIDENCE_THRESH:
                            detected_classes.add(p['class'])
                            self.defect_images.append(img_path)
                
        self.detection_info.setText("\n".join(detected_classes))
    
    def toggle_detections(self):
        pass


class HistoryTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        self.load_history()
        self.setLayout(layout)
    
    def load_history(self):
        self.history_list.clear()
        self.parent.cursor.execute("SELECT directory, timestamp FROM history ORDER BY id DESC")
        for directory, timestamp in self.parent.cursor.fetchall():
            item = QListWidgetItem(f"{timestamp}: {directory}")
            self.history_list.addItem(item)


class UserGuideTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Instructions on how to use the application."))
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoofInspectionApp()
    window.show()
    sys.exit(app.exec())