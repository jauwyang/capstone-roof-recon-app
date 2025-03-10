import sys
import os
import sqlite3
from datetime import datetime
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QScrollArea, QHBoxLayout, QStackedWidget, QSizePolicy, QTabWidget
)
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient




from detect_tab import DetectTab
from saved_image_sets_tab import SavedImageSetsTab
from guide_tab import GuideTab

CONFIDENCE_THRESH = 0.25

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roof Recon")
        self.setGeometry(100, 100, 1080, 720)  # sets initial dimensions of app when first opened

        main_layout = QVBoxLayout()
        main_layout.setObjectName("Main_Layout")

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(DetectTab(), "Detect")
        self.tab_widget.addTab(SavedImageSetsTab(), "Saved Image Sets")
        self.tab_widget.addTab(GuideTab(), "User Guide")
        
        # self.tab_widget.tabBar().setVisible(False)
