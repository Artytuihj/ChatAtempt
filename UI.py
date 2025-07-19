import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QListWidget, QGraphicsOpacityEffect, QSizePolicy, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, \
    pyqtSignal, QObject
from PyQt6.QtGui import QFont, QCursor


class SaladCord(QWidget,QObject):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ping 🍃")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #1A1A1A;")
        self.init_ui()

    buttonEvent = pyqtSignal(str)

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ------- Chat Feed Container -------
        self.chat_feed_container = QWidget()
        self.chat_feed_container.setStyleSheet("background-color: Transparent;")
        self.chat_feed_layout = QVBoxLayout(self.chat_feed_container)
        self.chat_feed_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_feed_layout.setSpacing(5)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_feed_container)
        self.scroll_area.setStyleSheet("border: none; background-color: Transparent;")
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chat_feed_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


        # ------- Input Field (Prompt) Container -------
        prompt_container = QWidget()
        prompt_layout = QHBoxLayout(prompt_container)
        prompt_layout.setContentsMargins(2, 0, 0, 2)
        prompt_layout.setSpacing(5)

        self.prompt = QTextEdit()
        self.prompt.setStyleSheet("""
            QTextEdit {
                border: 2px solid #292929;
                border-radius: 9px;
                background-color: #262626;
                font-size: 12px;
                color: white; 
            }
            QTextEdit:hover {
                background-color: #272727;
            }
            QTextEdit:focus {
                border-color: #2abf5e;
            }
            QTextEdit::placeholder {
                color: #3d3d3d;
                font-weight: bold;
            }
        """)
        self.prompt.setFixedHeight(30)
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt.setPlaceholderText("Type Your Message Here...")
        self.prompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.prompt.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        prompt_layout.addWidget(self.prompt)

        sendB = QPushButton("Send")
        sendB.setStyleSheet("""
            QPushButton {
                background-color: #2abf5e;
                border-radius: 9px;
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
        sendB.setFixedWidth(70)
        sendB.setFixedHeight(32)
        sendB.clicked.connect(lambda : self.buttonEvent.emit("send"))
        prompt_layout.addWidget(sendB)

        # ------- Chat Layout -------
        chat_container = QWidget()
        chat_container.setObjectName("chat_container")
        chat_container.setStyleSheet("""QWidget#chat_container {
                                    background-color: #1A1A1A;
                                    border: 2px solid #292929;
                                    border-radius: 9px;}""")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.addWidget(self.scroll_area)   # add scroll area, not container
        chat_layout.addWidget(prompt_container)

        main_layout.addWidget(chat_container)

    def three_dots(self):
        menu = QMenu()
        menu.setStyleSheet("""
               QMenu {
                   background-color: #1a1a1a;
                   color: white;
                   border: 2px solid #292929;
                   border-radius: 6px;
               }
               QMenu::item:selected {
                   background-color: #2abf5e;
                   border-radius: 6px;
                   color: black;
               }
           """)
        menu.addAction("Reply")
        menu.addAction("Delete")
        menu.exec(QCursor.pos())
    def send_message(self,nickname,text,msg_id):

            msg_widget = QWidget()
            msg_widget.setStyleSheet("""
                    QWidget {
                        background-color: transparent;
                        border-radius: 6px;
                    }
                    QWidget:hover {
                        background-color: #292929;
                    }
                """)

            layout = QVBoxLayout(msg_widget)
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(2)

            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)

            nickname_label = QLabel(f"{nickname}:")
            nickname_label.setStyleSheet("color: white; font-weight: bold;")
            top_row.addWidget(nickname_label)
            top_row.addStretch()

            three_dots_button = QPushButton("...")
            three_dots_button.setFixedSize(20, 20)
            three_dots_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #2abf5e;
                        border: none;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        color: #ffffff;
                    }
                """)
            three_dots_button.setProperty("msg_id", msg_id)
            three_dots_button.clicked.connect(self.three_dots)
            top_row.addWidget(three_dots_button)

            message_label = QLabel(text)
            message_label.setStyleSheet("color: white;")
            message_label.setWordWrap(True)

            layout.addLayout(top_row)
            layout.addWidget(message_label)
            self.chat_feed_layout.addWidget(msg_widget)
            self.prompt.clear()
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())


def ui_start():
    app = QApplication(sys.argv)

    scrollbar_style = """
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 12px;
            margin: 4px 0 4px 0;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #3d3d3d;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #2abf5e;
        }
        QScrollBar::handle:vertical:pressed {
            background: #239c4d;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QScrollBar:horizontal {
            border: none;
            background: transparent;
            height: 12px;
            margin: 0 4px 0 4px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #3d3d3d;
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #2abf5e;
        }
        QScrollBar::handle:horizontal:pressed {
            background: #239c4d;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    """
    app.setStyleSheet(app.styleSheet() + scrollbar_style)

    window = SaladCord()
    window.show()
    window.send_message("[SYSTEM]", "test test test", "0")
    return app,window




