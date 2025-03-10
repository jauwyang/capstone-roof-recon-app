import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

# cd "Desktop\Projects\Programs\uw-courses\capstone\roof-recon"
# python app.py

def main():
    app = QApplication(sys.argv)

    # Apply external stylesheet
    with open("ui/ui_styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()