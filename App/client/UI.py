import sys
from idlelib.configdialog import font_sample_text

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QListWidget, QGraphicsOpacityEffect, QSizePolicy, QScrollArea,
    QMenu, QDialog
)
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, \
    pyqtSignal, QObject
from PyQt6.QtGui import QFont, QCursor, QPalette, QColor
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
    buttonEvent = pyqtSignal(str, str)
    msgEvent = pyqtSignal(str, str, int, bool)
    regWindowEvent = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("thing no no work")
        self.resize(900, 600)
        self.setStyleSheet(f"background-color: {black};")
        self.init_ui()

        self.msgEvent.connect(self.send_message)
        self.regWindowEvent.connect(self.regWindow)

    def init_ui(self):
        try:
            self.main_layout = QHBoxLayout(self)

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
            self.prompt_container = QWidget()
            self.prompt_layout = QHBoxLayout(self.prompt_container)
            self.prompt_layout.setContentsMargins(2, 0, 0, 2)
            self.prompt_layout.setSpacing(5)

            # ------- msg prompt -------
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
            self.prompt_layout.addWidget(self.prompt)

            # ------- send button -------
            self.sendB = QPushButton("Send")
            self.sendB.setStyleSheet(f"""
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
            self.sendB.setFixedWidth(70)
            self.sendB.setFixedHeight(32)
            self.sendB.clicked.connect(lambda : self.buttonEvent.emit("send",self.prompt.toPlainText()))
            self.prompt_layout.addWidget(self.sendB)

            # ------- Chat Layout -------
            self.chat_container = QWidget()
            self.chat_container.setObjectName("chat_container")
            self.chat_container.setStyleSheet(f"""QWidget#chat_container {{
                                        background-color: {black};
                                        border: 2px solid {bg_quaternary};
                                        border-radius: 9px;}}""")
            self.chat_layout = QVBoxLayout(self.chat_container)
            self.chat_layout.setContentsMargins(10, 10, 10, 10)
            self.chat_layout.addWidget(self.scroll_area)   # add scroll area, not container
            self.chat_layout.addWidget(self.prompt_container)

            # -------- side bar --------
            self.side_bar_container = QWidget()
            self.side_bar_container.setStyleSheet(f"""QWidget {{
                                                    background-color: {bg_tertiary};
                                                    border-radius: 9px;}}""")
            self.side_bar_layout = QVBoxLayout(self.side_bar_container)
            self.side_bar_layout.setContentsMargins(5, 5, 5, 5)
            self.side_bar_layout.setSpacing(1)

            # -------- Host button --------
            self.hostB = QPushButton("Host")
            self.hostB.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {primary_green};
                            border-radius: 9px;
                            font-size: 12px;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: {primary_green_hover};
                        }}
                        QPushButton:pressed {{
                            background-color: {primary_green_dark};
                            padding-top:  2px;
                            padding-left: 2px;
                        }}
                    """)
            self.hostB.setFixedHeight(32)
            self.hostB.setFixedWidth(32)
            self.hostB.clicked.connect(lambda : self.buttonEvent.emit("host","Server"))
            self.side_bar_layout.addWidget(self.hostB, alignment=Qt.AlignmentFlag.AlignTop)

            # -------- Host button --------
            self.connB = QPushButton("conn")
            self.connB.setStyleSheet(f"""
                                QPushButton {{
                                    background-color: {primary_green};
                                    border-radius: 9px;
                                    font-size: 12px;
                                    font-weight: bold;
                                }}
                                QPushButton:hover {{
                                    background-color: {primary_green_hover};
                                }}
                                QPushButton:pressed {{
                                    background-color: {primary_green_dark};
                                    padding-top:  2px;
                                    padding-left: 2px;
                                }}
                            """)
            self.connB.setFixedHeight(32)
            self.connB.setFixedWidth(32)
            self.connB.clicked.connect(lambda: self.buttonEvent.emit("connReq",""))
            self.side_bar_layout.addWidget(self.connB, alignment=Qt.AlignmentFlag.AlignTop)


        finally:
            self.main_layout.addWidget(self.side_bar_container)
            self.main_layout.addWidget(self.chat_container)

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

    def send_message(self, nickname, text, msg_id,isDeliverd):
        try:
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
            msg_widget.setProperty("msg_id", msg_id)
            msg_widget.setProperty("is_deliverd", isDeliverd)

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
                        color: {primary_green};
                        border: none;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        color: {interactive_active};
                        
                    }}
                """)
            three_dots_button.clicked.connect(self.three_dots)
            top_row.addWidget(three_dots_button)
            deliverdMark = QLabel("✓")
            deliverdMark.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }}
    
            """)
            palette = deliverdMark.palette()  # get the current palette
            palette.setColor(QPalette.ColorRole.WindowText, QColor(interactive_normal))
            deliverdMark.setPalette(palette)
            if isDeliverd:
                palette.setColor(QPalette.ColorRole.WindowText, QColor(interactive_hover))
                deliverdMark.setPalette(palette)
            message_label = QLabel(text)
            message_label.setStyleSheet(f"color: {interactive_active};")
            message_label.setWordWrap(True)
            top_row.addWidget(deliverdMark)
            layout.addLayout(top_row)
            layout.addWidget(message_label)
            self.chat_feed_layout.addWidget(msg_widget)
            self.prompt.clear()
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        finally:
            return

    def regWindow(self):

        if hasattr(self, 'regWindowContainer') and self.regWindowContainer.isVisible():
            self.regWindowContainer.show()
            self.regWindowContainer.raise_()
        else:
            # Create the popup widget
            self.regWindowContainer = QWidget(self)
            self.regWindowContainer.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_secondary};
                    border-radius: 9px;
                }}
            """)
            self.regWindowContainer.setWindowFlags(Qt.WindowType.SubWindow)  # float above main layout
            self.regWindowContainer.resize(200, 100)

            # Create layout inside the widget
            layout = QVBoxLayout(self.regWindowContainer)
            layout.setContentsMargins(5, 5, 5, 5)

            # Center inside the main window
            parent_width = self.width()
            parent_height = self.height()
            px = (parent_width - 200) // 2
            py = (parent_height - 100) // 2
            self.regWindowContainer.move(px, py)

            self.regWindowContainer.show()
            self.regWindowContainer.raise_()

            # --------- label -----------
            label = QLabel("Enter Code",alignment=Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(f"color: {primary_green_dark};")
            font = QFont()
            font.setFamily("Arial")
            font.setPointSize(20)
            font.setBold(True)
            label.setFont(font)

            label.show()
            layout.addWidget(label)
            # --------- Code prompt ----------
            self.codePrompt = QTextEdit()
            self.codePrompt.setStyleSheet(f"""
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
            self.codePrompt.setFixedHeight(30)
            self.codePrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.codePrompt.setPlaceholderText("Enter code here")
            self.codePrompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.codePrompt.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
            layout.addWidget(self.codePrompt)
            # -------- Host button --------
            connB = QPushButton("Connect")
            connB.setStyleSheet(f"""
                QPushButton {{
                    background-color: {primary_green};
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
                    padding-left: 2px;
                }}
            """)
            connB.setFixedSize(90, 20)  # sets width and height at once
            connB.clicked.connect(lambda: self.buttonEvent.emit("conn",self.codePrompt.toPlainText()))

            # set alignment here
            layout.addWidget(connB, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)




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
    window.send_message("[SYSTEM]", "test test test", "0",False)
    return app,window




