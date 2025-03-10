from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFileDialog
from PyQt6.QtCore import Qt

class DetectTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setObjectName("Tabs")

        button_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Upload Image Set")
        self.predict_btn = QPushButton("Predict Image Set")
        self.toggle_btn = QPushButton("Toggle Detections")
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.predict_btn)
        button_layout.addWidget(self.toggle_btn)
        layout.addLayout(button_layout)

        self.upload_btn.clicked.connect(self.load_directory)
        # self.predict_btn.clicked.connect(self.run_model_on_directory)
        # self.toggle_btn.clicked.connect(self.toggle_detections)


        # Create a Scroll Area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # Allows content to resize

        # Create a container widget that will hold the scrollable content
        content_widget = QWidget()
        content_widget.setObjectName("ScrollContent")  # Useful for styling

        # Set layout for content widget
        content_layout = QHBoxLayout(content_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Add multiple buttons to simulate content
        for i in range(40):  # Adding multiple widgets
            content_layout.addWidget(QPushButton(f"Item {i+1}"))

        # Set the content widget inside the scroll area
        scroll_area.setWidget(content_widget)

        # Add scroll area to the main layout
        layout.addWidget(scroll_area)

        





    def load_directory(self):
        self.dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")







        # main_layout = QVBoxLayout()

        # # Button Tabs
        # button_layout = QHBoxLayout()
        # button_layout.setObjectName("Tab_Buttons_Block")

        # self.tab_detect = QPushButton("Detect")
        # self.tab_history = QPushButton("History")
        # self.tab_guide = QPushButton("User Guide")

        # self.tab_detect.setObjectName("Tabs")
        # self.tab_history.setObjectName("Tabs")
        # self.tab_guide.setObjectName("Tabs")

        # self.tab_detect.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.tab_history.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.tab_guide.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # self.tab_detect.setCheckable(True)
        # self.tab_history.setCheckable(True)
        # self.tab_guide.setCheckable(True)

        # self.tab_detect.setChecked(True)

        # button_layout.addWidget(self.tab_detect)
        # button_layout.addWidget(self.tab_history)
        # button_layout.addWidget(self.tab_guide)

        # main_layout.addLayout(button_layout)