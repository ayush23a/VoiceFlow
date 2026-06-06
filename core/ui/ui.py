import socket
import sys

from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer

HOST = "127.0.0.1"
PORT = 65433


class Bubble(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.label = QLabel("", self)

        self.label.setStyleSheet("""
            background-color: rgba(30, 30, 30, 220);
            color: white;
            font-size: 20px;
            padding: 15px 25px;
            border-radius: 20px;
        """)

        self.hide()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server.bind((HOST, PORT))

        self.server.listen()

        self.server.setblocking(False)

        self.timer = QTimer()

        self.timer.timeout.connect(self.check_messages)

        self.timer.start(100)

    def check_messages(self):
        try:
            conn, addr = self.server.accept()

            with conn:
                message = conn.recv(1024).decode()

                self.update_message(message)

        except BlockingIOError:
            pass

    def update_message(self, message):
        if message == "hide":
            self.hide()
            return

        self.label.setText(message)

        self.label.adjustSize()

        self.resize(self.label.size())

        screen = QApplication.primaryScreen().geometry()

        x = screen.width() - self.width() - 50
        y = screen.height() - self.height() - 100

        self.move(x, y)

        self.show()


app = QApplication(sys.argv)

bubble = Bubble()

sys.exit(app.exec())