# main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QRadioButton,
    QPushButton, QGroupBox, QLabel
)
from PyQt6.QtGui  import QFont
from PyQt6.QtCore import Qt, QSize

# Import your two calculator windows directly:
from two.main   import TwoMainWindow   # two/main.py defines class TwoWindow(QMainWindow)
from three.main import MainWindow # three/main.py defines class ThreeWindow(QMainWindow)

class MatrixSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.child = None
        self.init_ui()

    def init_ui(self):
        # Font
        QApplication.setFont(QFont('Lucida Console', 12))

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Title
        title = QLabel("Matrix Calculator", self)
        title.setFont(QFont('Lucida Console', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2E86C1; margin-bottom: 30px;")
        layout.addWidget(title)

        # Radio group
        box = QGroupBox("Select Matrix Size", self)
        box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498DB;
                border-radius: 15px;
                margin-top: 20px;
                padding-top: 15px;
                color: #2E86C1;
                font-weight: bold;
            }
        """)
        v = QVBoxLayout(box)
        self.radio2 = QRadioButton("2×2 Matrix", box)
        self.radio3 = QRadioButton("3×3 Matrix", box)
        self.radio2.setChecked(True)
        for r in (self.radio2, self.radio3):
            r.setStyleSheet("""
                QRadioButton {
                    color: #5D6D7E;
                    padding: 8px;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            v.addWidget(r)
        layout.addWidget(box)

        # OK button
        btn = QPushButton("OK", self)
        btn.setFixedSize(QSize(120, 40))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2E86C1; }
            QPushButton:pressed { background-color: #21618C; }
        """)
        btn.clicked.connect(self.launch_calculator)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Window
        self.setWindowTitle("Matrix Calculator Launcher")
        self.setFixedSize(400, 300)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def launch_calculator(self):
        # pick the class, create & show it on the same event loop:
        if self.radio2.isChecked():
            self.child = TwoMainWindow()
        else:
            self.child = MainWindow()

        self.child.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MatrixSelector()
    w.show()
    sys.exit(app.exec())
