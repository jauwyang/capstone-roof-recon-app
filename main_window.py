import os
from assets.roof_recon_designerqt_ui import Ui_MainWindow
from imageSetDB import *
from PyQt6.QtGui import QPixmap, QPen, QColor, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QInputDialog, QMainWindow, QFileDialog, QPushButton, QWidget, QScrollArea, 
    QGridLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
    QDialog, QListWidget, QListWidgetItem, QVBoxLayout, QProgressBar, QMessageBox,
    QListView, QAbstractItemView, QTableWidget, QTableWidgetItem
)
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
        self.curr_set_id = None

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

        self.filterAllImagesButton.clicked.connect(lambda: self._displayImageSet("all"))
        self.filterDamagedImagesButton.clicked.connect(lambda: self._displayImageSet("damaged"))
        self.filterUndamagedImagesButton.clicked.connect(lambda: self._displayImageSet("undamaged"))

        # Current Image
        self.currentImageView = self.detectTab.findChild(QGraphicsView, "CurrentImage")
        self.currentImageScene = QGraphicsScene()
        self.currentImageView.setScene(self.currentImageScene)

        # Predict Model
        self.detectImageSet = self.detectTab.findChild(QPushButton, "DetectImageSet")
        self.detectImageSet.clicked.connect(self.predictDamages)
        self.modelProgressBar = self.detectTab.findChild(QProgressBar, "modelProgressBar")
        self.modelProgressBar.setValue(0)

        # Damage Information List
        self.damageInformationList = self.detectTab.findChild(QListWidget, "DamageInformationList")


        # Tab 2
        self.savedImageSetsTab = self.findChild(QWidget, "SavedImageSetsTab")
        self.loadImageSetButton_tab2 = self.savedImageSetsTab.findChild(QPushButton, "LoadImageSet")
        self.deleteImageSetButton_tab2 = self.savedImageSetsTab.findChild(QPushButton, "DeleteImageSet")

        self.imageSetTable = self.savedImageSetsTab.findChild(QTableWidget, "ImageSetTable")
        self.imageSetTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.imageSetTable.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.imageSetTable.itemSelectionChanged.connect(self.handleSelectionChange)

        # Load Image Sets in Table
        self.updateImageSetTable()
        self.loadImageSetButton_tab2.setEnabled(False)  # Initially disable load button
        self.loadImageSetButton_tab2.clicked.connect(self.loadPreviousImageSetHandler)

        # Delete Image Sets in Table
        self.deleteImageSetButton_tab2.setEnabled(False)
        self.deleteImageSetButton_tab2.clicked.connect(self.deleteSelectedImageSet)

    def deleteSelectedImageSet(self):
        selected_row = self.imageSetTable.currentRow()
        
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an image set to delete.")
            return

        # Get the Image Set ID from the hidden column
        set_id = int(self.imageSetTable.item(selected_row, 3).text())
        set_name = self.imageSetTable.item(selected_row, 0).text()

        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                    f"Are you sure you want to delete this image set: {set_name}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            try:
                # Delete Predictions
                cursor.execute("SELECT id FROM images WHERE image_set_id = ?", (set_id,))
                image_ids = [row[0] for row in cursor.fetchall()]
                cursor.executemany("DELETE FROM predictions WHERE image_id = ?", [(img_id,) for img_id in image_ids])

                # Delete from images table first (to maintain foreign key constraints)
                cursor.execute("DELETE FROM images WHERE image_set_id = ?", (set_id,))
                
                # Now delete the image set itself
                cursor.execute("DELETE FROM image_sets WHERE id = ?", (set_id,))
                
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete image set: {e}")
                conn.rollback()
            finally:
                conn.close()

            # Remove from QTableWidget
            self.imageSetTable.removeRow(selected_row)
            self.curr_dir_path = None
            self.curr_set_id = None

            self.updateImageSetTable()  # Refresh table after deleting

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Roof Recon")
            msg_box.setText("Successfully deleted image set. Please load a new one to proceed")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()


    def loadNewImageSetHandler(self):
        dir_path = self._loadDirectoryHandler()
        if not dir_path:
            return
        
        # Ask the user for a custom dataset name
        dataset_name, ok = QInputDialog.getText(self, "Roof Recon", "Enter a name/address for this image set:")
        if not ok or not dataset_name.strip():
            QMessageBox.warning(self, "Invalid Name", "Dataset name cannot be empty.")
            return
        dataset_name = dataset_name.strip()  # Remove spaces
        self.curr_set_id = add_image_set(dataset_name, dir_path)
        

        self.curr_dir_path = dir_path
        image_names = [f for f in os.listdir(dir_path) if f.endswith(('.png', '.jpg', '.jpeg', '.JPG'))]
        
        # Upload Images to DB under a new dir name (initalize all with no damages)
        add_images_to_set(self.curr_set_id, dir_path, image_names)  # will always be 0
        self.updateImageSetTable()

        # Load Images
        self._displayImageSet(filter_status="all")


    def loadPreviousImageSetHandler(self):
        selected_row = self.imageSetTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an image set first.")
            return

        set_id = int(self.imageSetTable.item(selected_row, 3).text())  # Get hidden set_id

        print(f"Loading Image Set ID: {set_id}")

        # Update current set ID and load images
        self.curr_set_id = set_id
        self._displayImageSet(filter_status="all")  # Load all images

    def _displayImageSet(self, filter_status):
        if not self.curr_set_id:
            print("No Image Set selected!")
            self.displayWarningNoImageSetLoadedMessage()
            return
        if filter_status == "all":
            images = get_all_images_from_set(self.curr_set_id)
        elif filter_status == "damaged":
            images = get_damaged_images_from_set(self.curr_set_id)
        elif filter_status == "undamaged":
            images = get_no_damage_images_from_set(self.curr_set_id)
        else:
            print("Error with selected filter")
            return

        # print(images)


        """Displays images inside the scrollable area."""
        # Clear existing images
        for i in reversed(range(self.currentImageSetGrid.count())):
            self.currentImageSetGrid.itemAt(i).widget().deleteLater()

        # Populate the grid with images
        row, col = 0, 0
        for image in images:
            image_id = image[0]
            image_name = image[1]
            dir_path = image[2]
            image_path = os.path.join(dir_path, image_name)
            label = QLabel()
            pixmap = QPixmap(image_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)  # Resize for UI
            label.setPixmap(pixmap)
            self.currentImageSetGrid.addWidget(label, row, col)
            label.mousePressEvent = lambda event, dir=dir_path, img_name=image_name, img_id=image_id : self.display_selected_image(dir, img_name, img_id)

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
        
    def display_selected_image(self, dir_path, image_name, img_id):
        image_path = os.path.join(dir_path, image_name)
        pixmap = QPixmap(image_path)
        self.currentImageScene.clear()  # Remove any existing image
        self.currentImageScene.addPixmap(pixmap)
        self.currentImageView.fitInView(self.currentImageScene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

        results = get_predictions_for_image(img_id)
        
        if len(results) > 0:
            self.drawBoundingBoxes(results)
        self.updateDamageInformationList(results)

    def predictDamages(self):
        if not self.curr_set_id:
            print("No Image Set selected!")
            self.displayWarningNoImageSetLoadedMessage()
            return
        
        image_queries = get_all_images_from_set(self.curr_set_id)
        image_names = [image_query[1] for image_query in image_queries]
        image_ids = [image_query[0] for image_query in image_queries]
        
        dir_path = image_queries[0][2]

        print("Starting Predictions...")

        self.modelProgressBar.setMinimum(0)
        self.modelProgressBar.setMaximum(len(image_names))

        self.model.predict(dir_path, image_names, image_ids, self.modelProgressBar)
        self.createPredictionPopup()
        print("Finished Predictions!")
        self.modelProgressBar.setValue(0)


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

    def createPredictionPopup(self):
        popup = QDialog()
        popup.setWindowTitle("Roof Recon")
        popup.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        label = QLabel("Completed detection for image set.", popup)
        layout.addWidget(label)        

        close_button = QPushButton("Ok", popup)
        close_button.clicked.connect(popup.close)  # Close when clicked
        layout.addWidget(close_button)

        popup.setLayout(layout)
        popup.exec()  # Show the popup



    def updateImageSetTable(self):
        image_sets = get_all_image_sets()  # Fetch (id, name, directory, timestamp) from DB
        self.imageSetTable.setRowCount(len(image_sets))
        self.imageSetTable.setColumnCount(4)  # Extra column for set_id (hidden)

        self.imageSetTable.setHorizontalHeaderLabels(["Name", "Directory", "Timestamp", "ID"])
        
        for row, (set_id, name, dir_path, timestamp) in enumerate(image_sets):
            self.imageSetTable.setItem(row, 0, QTableWidgetItem(name))
            self.imageSetTable.setItem(row, 1, QTableWidgetItem(dir_path))
            self.imageSetTable.setItem(row, 2, QTableWidgetItem(timestamp))
            
            id_item = QTableWidgetItem(str(set_id))
            id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Prevent editing
            self.imageSetTable.setItem(row, 3, id_item)

        # Hide the ID column (column index 3)
        self.imageSetTable.setColumnHidden(3, True)


    def handleSelectionChange(self):
        selected_row = self.imageSetTable.currentRow()
        self.loadImageSetButton_tab2.setEnabled(selected_row != -1)  # Enable if a row is selected
        self.deleteImageSetButton_tab2.setEnabled(selected_row != -1)

    def displayWarningNoImageSetLoadedMessage(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Roof Recon")
        msg_box.setText("An image set has not been selected. Please load an image set to perform this action.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()