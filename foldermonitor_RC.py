import os
import subprocess
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FileHandler(FileSystemEventHandler):
    def __init__(self, batch_getter):
        super().__init__()
        self._batch_getter = batch_getter

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"New file created: {file_path}")
        batch_path = self._batch_getter()
        if not batch_path:
            print("Batch file path is not set; skipping execution.")
            return
        try:
            subprocess.run([batch_path], shell=True, check=False)
        except OSError as exc:
            print(f"Failed to run batch file: {exc}")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reality Capture Watchdog App")

        self.path_edit = QLineEdit(self)
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Select a directory")

        self.batch_edit = QLineEdit(self)
        self.batch_edit.setReadOnly(True)

        directory_label = QLabel("Choose a directory:", self)
        directory_button = QPushButton("Browse", self)
        directory_button.clicked.connect(self.browse_path)

        batch_label = QLabel("Choose a batch file:", self)
        batch_button = QPushButton("Browse", self)
        batch_button.clicked.connect(self.browse_batch_file)

        start_button = QPushButton("Start Monitoring", self)
        start_button.setStyleSheet("background-color: green; color: white;")
        start_button.clicked.connect(self.start_monitoring)

        layout = QVBoxLayout()
        layout.addWidget(directory_label)
        layout.addWidget(self.path_edit)
        layout.addWidget(directory_button)
        layout.addWidget(batch_label)
        layout.addWidget(self.batch_edit)
        layout.addWidget(batch_button)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.observer: Optional[Observer] = None
        self.event_handler = FileHandler(self._get_batch_path)

    def browse_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.path_edit.setText(directory)

    def browse_batch_file(self):
        batch_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Batch File",
            "",
            "Batch Files (*.bat);;All Files (*)",
        )
        if batch_file:
            self.batch_edit.setText(batch_file)

    def start_monitoring(self):
        directory = self.path_edit.text().strip()
        if not os.path.isdir(directory):
            QMessageBox.critical(self, "Error", "Please select a valid directory.")
            return

        batch_file = self.batch_edit.text().strip()
        if not os.path.isfile(batch_file):
            QMessageBox.critical(self, "Error", "Please select a valid batch file.")
            return

        if self.observer and self.observer.is_alive():
            self._stop_observer()

        self.observer = Observer()
        self.observer.schedule(self.event_handler, directory, recursive=False)
        self.observer.start()
        QMessageBox.information(self, "Info", f"Monitoring directory: {directory}")

    def _stop_observer(self):
        if not self.observer:
            return
        self.observer.stop()
        self.observer.join(timeout=5)
        self.observer = None

    def _get_batch_path(self) -> str:
        return self.batch_edit.text().strip()

    def closeEvent(self, event):
        self._stop_observer()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec()
