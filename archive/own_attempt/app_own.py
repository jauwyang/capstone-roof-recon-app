import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

# cd "Desktop\Projects\Programs\uw-courses\capstone\roof-recon"
# python app.py

# python own_attempt/app_own.py

def main():
    app = QApplication(sys.argv)
    with open("own_attempt/ui/styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
