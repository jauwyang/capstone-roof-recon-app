import os
from assets.roof_recon_designerqt_ui import Ui_MainWindow
from imageSetDB import *
from PyQt6.QtGui import QPixmap, QPen, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QWidget, QScrollArea, QGridLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from model import RoofDetectionModel


CLASS_INFO = {
    "Degranulation": {
        "name": "Degranulation",
        "color": QColor("red"),
        "details": [
            "Potential Causes: Aging, UV exposure, poor ventilation, or foot traffic",
            "Compromise/Severity: Exposes asphalt layer, leading to faster deterioration and potential leaks",
            "Granules protect the asphalt layer of shingles from UV rays",
            "Is common in older roofs (10+ years)",
            "Accelerates water absorption and heat retention, shortening roof lifespan",
            "If minimal, apply a roof sealant to slow further granule loss",
            "If extensive, replace affected shingles or consider a roof coating",
            "Improve attic ventilation to reduce heat damage over time"
        ],
    },
    "Puncture": {
        "name": "Puncture",
        "color": QColor("green"),
        "details": [
            "Potential Causes: Fallen debris, improper installation, foot traffic, or animal activity",
            "Compromise/Severity: Creates direct entry points for water, leading to leaks and structural damage",
            "Small punctures can grow over time due to weather exposure",
            "Often requires immediate patching or shingle replacement"
        ],
    },
    "Hail Impac": {
        "name": "Hail Impact",
        "color": QColor("blue"),
        "details": [
            "Potential Causes: Severe storms with hailstones 1”+ in diameter",
            "Compromise/Severity: Dents or cracks weaken shingles, making them prone to leaks and premature failure",
            "Damage may not be immediately visible but worsens over time",
            "Often requires immediate patching or shingle replacement",
            "Inspect for soft spots and replace any compromised shingles",
            "Apply roofing sealant if damage is superficial",
            "Contact insurance if widespread damage is present—hail damage is often covered"
        ],
    },
    "Cracked Shingle": {
        "name": "Cracked Shingle",
        "color": QColor("orange"),
        "details": [
            "Potential Causes: Thermal expansion/contraction, impact damage, or poor installation",
            "Compromise/Severity: Reduces shingle integrity, allowing water penetration and further cracking",
            "Often occurs in older shingles or extreme temperature conditions",
            "Can lead to curling or lifting if left unaddressed",
            "Small cracks: Seal with a roofing adhesive to prevent water infiltration",
            "Large cracks: Remove and replace the damaged shingle"
        ],
    },
    "Chipped Shingle": {
        "name": "Chipped Shingle",
        "color": QColor("purple"),
        "details": [
            "Potential Causes: Wind uplift, falling debris, aging, or impact stress",
            "Compromise/Severity: Minor chipping may not cause immediate leaks, but larger chips expose underlayers to moisture",
            "Can be an early sign of deteriorating shingles",
            "Frequent chipping indicates the need for a roof inspection",
            "If minor, apply roofing sealant to prevent further chipping",
            "If the chip exposes the asphalt layer, replace the shingle"
        ],
    },
}

# "Puncture": {
#         "name": ,
#         "color": ,
#         "information": [],
#     },



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = RoofDetectionModel(False)
        self.curr_dir_path = None

        # Tab 1
        self.detectTab = self.findChild(QWidget, "DetectTab")

        # Load Image Set
        self.loadNewImageSetButton = self.detectTab.findChild(QPushButton, "LoadNewImageSetBtn")
        self.loadNewImageSetButton.clicked.connect(self.loadNewImageSetHandler)

        # Image Set
        self.imageSetLoaded = False
        self.currentImageSet = self.detectTab.findChild(QScrollArea, "CurrentImageSetScrollArea")
        self.currentImageSetScrollContent = self.currentImageSet.findChild(QWidget, "CurrentImageSetScrollAreaScrollContent")
        self.currentImageSetGrid = QGridLayout(self.currentImageSetScrollContent)
        self.currentImageSetScrollContent.setLayout(self.currentImageSetGrid)

        # Filters
        self.filterAllImagesButton = self.detectTab.findChild(QPushButton, "AllImagesFilterBtn")
        self.filterDamagedImagesButton = self.detectTab.findChild(QPushButton, "DamagedImagesFilterBtn")
        self.filterUndamagedImagesButton = self.detectTab.findChild(QPushButton, "UndamagedImagesFilterBtn")

        self.filterAllImagesButton.clicked.connect(lambda: self._displayImageSet(self.curr_dir_path, "all"))
        self.filterDamagedImagesButton.clicked.connect(lambda: self._displayImageSet(self.curr_dir_path, "damaged"))
        self.filterUndamagedImagesButton.clicked.connect(lambda: self._displayImageSet(self.curr_dir_path, "undamaged"))

        # Current Image
        self.currentImageView = self.detectTab.findChild(QGraphicsView, "CurrentImage")
        self.currentImageScene = QGraphicsScene()
        self.currentImageView.setScene(self.currentImageScene)

        # Predict Model
        self.detectImageSet = self.detectTab.findChild(QPushButton, "DetectImageSet")
        self.detectImageSet.clicked.connect(self.predictDamages)

        # Damage Information List
        self.damageInformationList = self.detectTab.findChild(QListWidget, "DamageInformationList")

        # Tab 2

    def loadNewImageSetHandler(self):
        dir_path = self._loadDirectoryHandler()
        if not dir_path:
            return
        
        self.curr_dir_path = dir_path
        
        image_names = [f for f in os.listdir(dir_path) if f.endswith(('.png', '.jpg', '.jpeg', '.JPG'))]
        
        # Upload Images to DB under a new dir name (initalize all with no damages)
        add_images_without_damage(dir_path, image_names)

        # Load Images
        self._displayImageSet(dir_path, filter_status="all")

    def _displayImageSet(self, dir_path, filter_status):
        if not dir_path:
            print("No Image Set selected!")
            return

        if filter_status == "all":
            images = get_all_images_from_dir(dir_path)
        elif filter_status == "damaged":
            images = get_damaged_images_from_dir(dir_path)
        elif filter_status == "undamaged":
            images = get_no_damage_images_from_dir(dir_path)
        else:
            print("Error with selected filter")
            return



        """Displays images inside the scrollable area."""
        # Clear existing images
        for i in reversed(range(self.currentImageSetGrid.count())):
            self.currentImageSetGrid.itemAt(i).widget().deleteLater()

        # Populate the grid with images
        row, col = 0, 0
        for image in images:
            image_name = image[1]
            image_path = os.path.join(dir_path, image_name)
            label = QLabel()
            pixmap = QPixmap(image_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)  # Resize for UI
            label.setPixmap(pixmap)
            self.currentImageSetGrid.addWidget(label, row, col)
            label.mousePressEvent = lambda event, dir=dir_path, img_name=image_name : self.display_selected_image(dir, img_name)

            col += 1
            if col > 3:  # 4 images per row
                col = 0
                row += 1

        # print(images)

    def _loadDirectoryHandler(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if not os.path.exists(dir_path):
            print(f"Directory: '{dir_path}' does not exist!")
            return
        
        return dir_path
        
    def display_selected_image(self, dir_path, image_name):
        image_path = os.path.join(dir_path, image_name)
        pixmap = QPixmap(image_path)
        self.currentImageScene.clear()  # Remove any existing image
        self.currentImageScene.addPixmap(pixmap)
        self.currentImageView.fitInView(self.currentImageScene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

        results = get_predictions_for_image(self.curr_dir_path, image_name)
        
        if len(results) > 0:
            self.drawBoundingBoxes(results)
        self.updateDamageInformationList(results)

    def predictDamages(self):
        if not self.curr_dir_path:
            print("No Image Set selected!")
            return
        
        image_queries = get_all_images_from_dir(self.curr_dir_path)
        image_names = [image_query[1] for image_query in image_queries]

        print("Starting Predictions...")
        self.model.predict(self.curr_dir_path, image_names)
        print("Finished Predictions!")

    def drawBoundingBoxes(self, results):
        for damage in results:
            x, y, w, h, confidence, label, uuid = damage
            class_colour = CLASS_INFO[label]['color']
            
            # Create a bounding box rectangle
            rect = QGraphicsRectItem(x-w/2, y-h/2, w, h)
            rect.setPen(QPen(class_colour, 4))  # Red border for bounding box
            self.currentImageScene.addItem(rect)


    def updateDamageInformationList(self, results):
        self.damageInformationList.clear()

        damageClasses = set()
        for damage in results:  # find what defects are in the current image
            damageClasses.add(damage[5])

        for damageType in damageClasses:
            defect = CLASS_INFO[damageType]['name']
            details = CLASS_INFO[damageType]['details']
            formatted_text = f"{defect}\n" + "\n".join([f"   • {point}" for point in details])
            item = QListWidgetItem(formatted_text)  # Create a new QListWidgetItem
            color = CLASS_INFO[damageType]['color']  # Default to white if class not found
            item.setForeground(QColor(color))  # Step 3: Set text color to match bounding box
            self.damageInformationList.addItem(item)  # Add item to the list
