import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QFileDialog, QMessageBox, \
    QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from UI.PyQt6 import QTCSS
from PyQt6.QtGui import QFontDatabase

from functions import settings, memory


class ConsoleWidget(QWidget):
    closeSignal = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Console")
        self.setGeometry(100, 100, 600, 400)

        self.isNoCheckClose = False

        layout = QVBoxLayout(self)

        self.console = QPlainTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #2b2b2b; color: white;")
        layout.addWidget(self.console)

        self.bottomPanel = QWidget(self)
        bottom_layout = QHBoxLayout(self.bottomPanel)

        self.saveButton = QPushButton(memory.get("translate", {}).get("saveLogsToFile", "Save logs to file"), self)
        self.saveButton.setStyleSheet("background-color: #3a3a3a; color: #a1d68b; border-radius: 5px; padding: 8px;")
        self.saveButton.clicked.connect(self.save_logs)
        bottom_layout.addWidget(self.saveButton)

        layout.addWidget(self.bottomPanel)

        self.apply_styles()

    def closeEvent(self, a0):
        if not self.isNoCheckClose:
            self.closeSignal.emit()
        return super().closeEvent(a0)

    def apply_styles(self):
        self.setStyleSheet(QTCSS.dil_dark)

    def save_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save logs", "", "Text Files (*.txt)")

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.console.toPlainText())
                QMessageBox.information(self, "logs", memory.get("translate", {}).get("saveLogsMsg", "Logs has been saved!"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f':{memory.get("translate", {}).get("saveErrLogsMsg", "Could not save logs")} {e}')

    def add_log(self, log_message):
        self.console.appendPlainText(log_message)

    def set_console_text(self, text):
        cursor = self.console.textCursor()
        old = self.console.verticalScrollBar().value()
        is_at_bottom = self.console.verticalScrollBar().value() == self.console.verticalScrollBar().maximum()
        if self.console.toPlainText() != text:
            self.console.setPlainText(text[-3000:-1])
            self.text = text

        if is_at_bottom:
            self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        else:
            self.console.setTextCursor(cursor)
            self.console.verticalScrollBar().setValue(old)
