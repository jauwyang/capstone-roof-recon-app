import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

# cd "Desktop\Projects\Programs\uw-courses\capstone\roof-recon"
# python app.py

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()