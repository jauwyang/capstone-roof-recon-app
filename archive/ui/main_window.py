from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QMessageBox, QListWidget
from PyQt5.QtGui import QPixmap, QFont, QCursor
from PyQt5.QtCore import Qt
import os
from core.model import RoofInspectionModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Roof Recon")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1E1E1E; color: #EEEEEE;")

        self.model = RoofInspectionModel()

        # Directory Label
        self.dir_label = QLabel("📂 Select Image Directory", self)
        self.dir_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.dir_label.setAlignment(Qt.AlignCenter)

        # Select Directory Button
        self.btn_select_dir = QPushButton("Choose Folder", self)
        self.btn_select_dir.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_select_dir.setCursor(QCursor(Qt.PointingHandCursor))  # 🔹 Cursor change
        self.btn_select_dir.clicked.connect(self.select_directory)

        # Process Button
        self.btn_process = QPushButton("🚀 Analyze Images", self)
        self.btn_process.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_process.setCursor(QCursor(Qt.PointingHandCursor))  # 🔹 Cursor change
        self.btn_process.setEnabled(False)
        self.btn_process.clicked.connect(self.process_images)

        # Image List
        self.image_list = QListWidget(self)
        self.image_list.setStyleSheet("background-color: #292929; color: #FFFFFF; border-radius: 10px; padding: 5px;")
        self.image_list.itemClicked.connect(self.show_image_info)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.dir_label)
        layout.addWidget(self.btn_select_dir)
        layout.addWidget(self.btn_process)
        layout.addWidget(self.image_list)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_dir = None

    def select_directory(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder_path:
            self.image_dir = folder_path
            self.dir_label.setText(f"📂 Selected: {os.path.basename(folder_path)}")
            self.btn_process.setEnabled(True)

    def process_images(self):
        if self.image_dir:
            results = self.model.run_inference_on_directory(self.image_dir)
            self.image_list.clear()
            for img_name, defects in results.items():
                self.image_list.addItem(f"{img_name}: {', '.join(defects)}")

            QMessageBox.information(self, "Processing Complete", "Roof inspection completed! Check the reports folder.")

    def show_image_info(self, item):
        img_name = item.text().split(":")[0]
        defect_details = self.model.get_defect_details(img_name)

        msg = QMessageBox(self)
        msg.setWindowTitle("📝 Defect Report")
        msg.setText(defect_details)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()