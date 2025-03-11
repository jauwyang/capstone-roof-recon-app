from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class GuideTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setObjectName("Tabs")
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