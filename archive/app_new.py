import sys
import os
import sqlite3
from datetime import datetime
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QFileDialog, QTabWidget, QListWidget, QListWidgetItem, QScrollArea, QGridLayout
)
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient  # Import the Roboflow SDK

CONFIDENCE_THRESH = 0.25

class RoofInspectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roof Inspection AI")
        self.setGeometry(100, 100, 1200, 800)

        # Set to True if using local model, False for Roboflow API
        self.use_local_model = False  # Change this flag to switch between local and Roboflow

        # Initialize the model
        if self.use_local_model:
            self.model = YOLO("best.pt")  # Load local YOLO model
        else:
            self.CLIENT = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key="eyy15gP8oZtUIzN3KfRC"  # Replace with your actual API key
            )
        
        # Initialize SQLite database
        self.init_db()

        # Main layout with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Tabs
        self.main_tab = MainTab(self)
        self.history_tab = HistoryTab(self)
        self.how_to_use_tab = HowToUseTab()
        
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.how_to_use_tab, "How to Use")
    
    def init_db(self):
        self.conn = sqlite3.connect("inspection_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                            (id INTEGER PRIMARY KEY, directory TEXT, timestamp TEXT)''')
        self.conn.commit()

    def add_to_history(self, directory):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO history (directory, timestamp) VALUES (?, ?)", (directory, timestamp))
        self.conn.commit()
        self.history_tab.load_history()


class MainTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.defect_images = []
        self.grid_mode = True
        
        layout = QVBoxLayout()
        
        # Load Directory Button
        self.load_btn = QPushButton("Load Directory & Run Model")
        self.load_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.load_btn.clicked.connect(self.load_directory)
        layout.addWidget(self.load_btn)
        
        # Image display area
        self.image_display = QLabel("Select an image")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_display)
        
        # Toggle Grid View
        self.toggle_btn = QPushButton("Toggle Grid/List View")
        self.toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_btn.clicked.connect(self.toggle_view)
        layout.addWidget(self.toggle_btn)
        
        # Scroll Area for Defective Images
        self.scroll_area = QScrollArea()
        self.image_list_widget = QWidget()
        self.image_list_layout = QGridLayout()
        self.image_list_widget.setLayout(self.image_list_layout)
        self.scroll_area.setWidget(self.image_list_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
    
    def load_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.run_model_on_directory(dir_path)
            self.parent.add_to_history(dir_path)
    
    def run_model_on_directory(self, dir_path):
        self.defect_images.clear()
        for file in os.listdir(dir_path):
            if file.endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(dir_path, file)
                if self.parent.use_local_model:
                    # Local model inference
                    results = self.parent.model(img_path)
                    if len(results[0].boxes) > 0:
                        self.defect_images.append(img_path)
                else:
                    # Roboflow API inference
                    result = self.parent.CLIENT.infer(img_path, model_id="roof-damage-detection-7zpct-xitjh/2")
                    predictions = result['predictions']
                    print("AAAAAAAAAAAAA")
                    print(predictions)
                    all_observed_classes = set()
                    for prediction in predictions:
                        class_name = prediction['class']
                        confidence = prediction['confidence']
                        if confidence > CONFIDENCE_THRESH:  # Only add if confidence is above 50%
                            self.defect_images.append(img_path)
                            all_observed_classes.add(class_name)

                    print(all_observed_classes)
                self.update_image_list()
    
    def update_image_list(self):
        for i in reversed(range(self.image_list_layout.count())):
            self.image_list_layout.itemAt(i).widget().setParent(None)
        
        for index, img_path in enumerate(self.defect_images):
            pixmap = QPixmap(img_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.mousePressEvent = lambda event, path=img_path: self.display_large_image(path)
            self.image_list_layout.addWidget(img_label, index // 3, index % 3)
    
    def display_large_image(self, img_path):
        pixmap = QPixmap(img_path).scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_display.setPixmap(pixmap)
    
    def toggle_view(self):
        self.grid_mode = not self.grid_mode
        self.update_image_list()


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


class HowToUseTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        instructions = QLabel(""" 
        1. Click 'Load Directory & Run Model' to select a folder.
        2. The model will process images and detect defects.
        3. Images with detected defects will appear in the scrollable panel.
        4. Click on an image to enlarge it and see details.
        5. View past directories in the 'History' tab.
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoofInspectionApp()
    window.show()
    sys.exit(app.exec())