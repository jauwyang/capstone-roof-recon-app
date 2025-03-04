from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
import os
from core.model import AIModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Image Processing App")
        self.setGeometry(100, 100, 600, 400)

        self.model = AIModel()  # Load AI model

        # UI Elements
        self.label = QLabel("No image loaded", self)
        self.label.setStyleSheet("border: 1px solid black;")
        self.label.setFixedSize(300, 300)

        self.btn_load = QPushButton("Load Image", self)
        self.btn_load.clicked.connect(self.load_image)

        self.btn_process = QPushButton("Process Image", self)
        self.btn_process.clicked.connect(self.process_image)
        self.btn_process.setEnabled(False)  # Disabled until image is loaded

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.btn_process)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_path = None  # Store image path

    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.label.setPixmap(pixmap.scaled(300, 300))
            self.btn_process.setEnabled(True)  # Enable process button

    def process_image(self):
        if self.image_path:
            output_path = self.model.run_inference(self.image_path)
            pixmap = QPixmap(output_path)
            self.label.setPixmap(pixmap.scaled(300, 300))