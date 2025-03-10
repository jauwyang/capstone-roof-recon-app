from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class SavedImageSetsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Tabs")
        layout = QVBoxLayout(self)
        layout.addWidget(QPushButton("This is tab 2"))