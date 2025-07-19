import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QListWidget, QGraphicsOpacityEffect, QSizePolicy, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, \
    pyqtSignal, QObject
from PyQt6.QtGui import QFont, QCursor
import re
#region Colors
black = "#121212"
spotify_green = "#2abf5e"
primary_green = "#7CB342"
primary_green_hover = "#689F38"
primary_green_dark = "#598f32"
accent_green = "#8BC34A"
light_green = "#DCEDC8"

light_grey = "#3d3d3d"
bg_primary = "#36393F"
bg_secondary = "#2F3136"
bg_tertiary = "#202225"
bg_quaternary = "#292B2F"

text_primary = "#DCDDDE"
text_secondary = "#B9BBBE"
text_muted = "#72767D"
text_link = "#7CB342"

interactive_normal = "#B9BBBE"
interactive_hover = "#DCDDDE"
interactive_active = "#FFFFFF"

status_idle = "#FAA61A"
status_dnd = "#F04747"
status_invisible = "#747F8D"
#endregion

class SaladCord(QWidget, QObject):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ping 🍃")
        self.resize(900, 600)
        self.setStyleSheet(f"background-color: {black};")  # #1A1A1A approx black replaced by black variable
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
        self.prompt.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid {bg_quaternary};
                border-radius: 9px;
                background-color: #262626;
                font-size: 12px;
                color: {interactive_active};
            }}
            QTextEdit:hover {{
                background-color: #272727;
            }}
            QTextEdit:focus {{
                border-color: {primary_green};
            }}
            QTextEdit::placeholder {{
                color: {light_grey};
                font-weight: bold;
            }}
        """)
        self.prompt.setFixedHeight(30)
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt.setPlaceholderText("Type Your Message Here...")
        self.prompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.prompt.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        prompt_layout.addWidget(self.prompt)

        sendB = QPushButton("Send")
        sendB.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary_green};  /* swapped spotify green #2abf5e -> primary_green */
                border-radius: 9px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {primary_green_hover};
            }}
            QPushButton:pressed {{
                background-color: {primary_green_dark};
                padding-top: 2px;
                padding-left: 1px;
            }}
        """)
        sendB.setFixedWidth(70)
        sendB.setFixedHeight(32)
        sendB.clicked.connect(lambda : self.buttonEvent.emit("send"))
        prompt_layout.addWidget(sendB)

        # ------- Chat Layout -------
        chat_container = QWidget()
        chat_container.setObjectName("chat_container")
        chat_container.setStyleSheet(f"""QWidget#chat_container {{
                                    background-color: {black};
                                    border: 2px solid {bg_quaternary};
                                    border-radius: 9px;}}""")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.addWidget(self.scroll_area)   # add scroll area, not container
        chat_layout.addWidget(prompt_container)

        main_layout.addWidget(chat_container)

    def three_dots(self):
        menu = QMenu()
        menu.setStyleSheet(f"""
               QMenu {{
                   background-color: {black};
                   color: {interactive_active};
                   border: 2px solid {bg_quaternary};
                   border-radius: 6px;
               }}
               QMenu::item:selected {{
                   background-color: {primary_green};
                   border-radius: 6px;
                   color: black;
               }}
           """)
        menu.addAction("Reply")
        menu.addAction("Delete")
        menu.exec(QCursor.pos())

    def send_message(self, nickname, text, msg_id):
        msg_widget = QWidget()
        msg_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border-radius: 6px;
                }}
                QWidget:hover {{
                    background-color: {bg_quaternary};
                }}
            """)

        layout = QVBoxLayout(msg_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        nickname_label = QLabel(f"{nickname}:")
        nickname_label.setStyleSheet(f"color: {interactive_active}; font-weight: bold;")
        top_row.addWidget(nickname_label)
        top_row.addStretch()

        three_dots_button = QPushButton("...")
        three_dots_button.setFixedSize(20, 20)
        three_dots_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {primary_green};  /* spotify green replaced */
                    border: none;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    color: {interactive_active};
                }}
            """)
        three_dots_button.setProperty("msg_id", msg_id)
        three_dots_button.clicked.connect(self.three_dots)
        top_row.addWidget(three_dots_button)

        message_label = QLabel(text)
        message_label.setStyleSheet(f"color: {interactive_active};")
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




