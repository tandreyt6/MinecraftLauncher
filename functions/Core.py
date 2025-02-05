import json
import sys
from PyQt6.QtCore import QCoreApplication, QTimer
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt6.QtWidgets import QApplication

class SingleInstanceApp(QApplication):
    PORT = 45678

    def __init__(self, argv):
        super().__init__(argv)

    def startServer(self):
        self.server = QTcpServer(self)
        if not self.server.listen(QHostAddress("127.0.0.1"), self.PORT):
            sys.exit(1)

        self.server.newConnection.connect(self.on_new_connection)

    def on_new_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self.handle_message(socket))

    def handle_packet(self, packet: dict):
        pass

    def handle_message(self, socket):
        data = socket.readAll().data().decode()
        try:
            message = json.loads(data)
            if isinstance(message, dict):
                print("Get packet:", message)
                self.handle_packet(message)
            elif message == "ping":
                print("Get ping!")
        except json.JSONDecodeError:
            print("Error decode JSON")


if __name__ == "__main__":
    app = SingleInstanceApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = SingleInstanceApp(sys.argv)
    sys.exit(app.exec())
