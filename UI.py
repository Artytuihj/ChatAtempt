import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QListWidget,QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QPropertyAnimation, QEasingCurve,QParallelAnimationGroup
from PyQt6.QtGui import QFont

def Send():
    print("Pressed")

class SaladCord(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SaladCord 🍃")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #1A1A1A;")
        self.init_ui()



    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ------- Chat Feed Container -------
        chat_feed_container = QWidget()
        chat_feed_container.setStyleSheet("background-color: #151515;"
                                          "border-radius: 5px;")
        chatFeed_layout = QVBoxLayout(chat_feed_container)
        chatFeed_layout.setSpacing(5)

        # ------- Input Field (Prompt) Container -------
        prompt_container = QWidget()
        prompt_layout = QHBoxLayout(prompt_container)
        prompt_layout.setSpacing(5)

        self.labelE = QLineEdit()
        self.labelE.setStyleSheet("""
            QLineEdit {
                border: 2px solid #292929;
                border-radius: 9px;
                background-color: #1A1A1A;
                height: 30px;
                font-size: 12px;
                color: white; 
            }
            QLineEdit:hover {
                background-color: #272727;
            }
            QLineEdit:focus {
                border-color: #2abf5e;
            }
            QLineEdit::placeholder {
                color: #3d3d3d;
                font-weight: bold;
            }
        """)
        self.labelE.setFixedWidth(700)
        self.labelE.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelE.setPlaceholderText("Type Your Message Here...")
        prompt_layout.addWidget(self.labelE)

        self.sendB = QPushButton("Send")
        self.sendB.setStyleSheet("""
            QPushButton {
                background-color: #2abf5e;
                border-radius: 9px;
                height: 34px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #239c4d;
            }
            QPushButton:pressed {
                background-color: #197036;
                padding-top: 2px;
                padding-left: 1px;
            }
        """)
        self.sendB.setFixedWidth(70)
        self.sendB.clicked.connect(Send)
        prompt_layout.addWidget(self.sendB)

        # ------- Chat Layout -------
        chat_layout = QVBoxLayout()
        chat_layout.setSpacing(5)
        chat_layout.addWidget(chat_feed_container)
        chat_layout.addWidget(prompt_container)

        # Add the whole chat layout to the main layout
        main_layout.addLayout(chat_layout)


def main():
    app = QApplication(sys.argv)
    window = SaladCord()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()