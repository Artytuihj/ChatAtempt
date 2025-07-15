import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt


class SaladCord(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SaladCord 🍃")
        self.resize(900, 600)
        self.setStyleSheet(self.get_stylesheet())
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Server List (Discord left panel)
        self.server_list = QListWidget()
        self.server_list.setFixedWidth(70)
        for emoji in ["🍉", "🎮", "🎨", "💬"]:
            item = QListWidgetItem(emoji)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.server_list.addItem(item)

        # Channel List
        self.channel_list = QListWidget()
        self.channel_list.setFixedWidth(180)
        self.channel_list.addItems(["# general", "# memes", "# dev", "# voice-chat"])

        # Chat area
        chat_layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        chat_input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        chat_input_layout.addWidget(self.message_input)
        chat_input_layout.addWidget(send_btn)

        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(chat_input_layout)

        # Combine all panels
        main_layout.addWidget(self.server_list)
        main_layout.addWidget(self.channel_list)
        main_layout.addLayout(chat_layout)

    def send_message(self):
        msg = self.message_input.text().strip()
        if msg:
            self.chat_display.append(f"<b>You:</b> {msg}")
            self.message_input.clear()

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #1a1b1e;
            color: white;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        QListWidget {
            background-color: #141517;
            border: none;
            border-radius: 12px;
            padding: 5px;
        }
        QListWidget::item {
            background-color: transparent;
            padding: 10px;
            margin: 5px;
            border-radius: 12px;
        }
        QListWidget::item:selected {
            background-color: #7be062;
            color: black;
        }
        QTextEdit {
            background-color: #202124;
            border: none;
            border-radius: 12px;
            padding: 10px;
        }
        QLineEdit {
            background-color: #2a2c2f;
            border: 2px solid #7be062;
            border-radius: 12px;
            padding: 8px;
        }
        QPushButton {
            background-color: #7be062;
            color: black;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 12px;
            border: none;
        }
        QPushButton:hover {
            background-color: #a6ff91;
            box-shadow: 0 0 10px #a6ff91;
        }
        """

def main():
    app = QApplication(sys.argv)
    window = SaladCord()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
