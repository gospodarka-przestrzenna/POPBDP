# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2024 Wawrzyniec Zipser, Maciej Kamiński (maciej.kaminski@pwr.edu.pl)
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
###############################################################################
__author__ = 'Wawrzyniec Zipser, Maciej Kamiński Politechnika Wrocławska'


import os
import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from .utils.translations import _

class DataInitializationWorker(QThread):
    progress_updated = pyqtSignal(int)  # Signal to update progress bar
    download_completed = pyqtSignal()  # Signal when download completes
    download_failed = pyqtSignal(str)  # Signal when download fails

    def __init__(self, download_url, target_file):
        super().__init__()
        self.download_url = download_url
        self.target_file = target_file

    def run(self):
        """Download the file and update progress."""
        try:
            response = requests.get(self.download_url, stream=True, timeout=10)
            response.raise_for_status()  # Raise an error for HTTP issues

            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 1024 * 1024  # 1 MB chunks
            downloaded = 0

            with open(self.target_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        progress = int((downloaded / total_size) * 100)
                        self.progress_updated.emit(progress)

            self.download_completed.emit()
        except requests.exceptions.RequestException as e:
            self.download_failed.emit(str(e))

class DataInitializationDialog(QDialog):
    def __init__(self, data_file_path, download_url):
        super().__init__()

        self.data_file_path = data_file_path
        self.download_url = download_url


        # Main window setup
        self.setWindowTitle(_("Initializing Plugin"))
        self.resize(500, 150)

        # Label to display status messages
        self.status_label = QLabel(_("Checking database file..."))
        self.status_label.setAlignment(Qt.AlignCenter)

        # Progress bar to show download progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Cancel button
        self.cancel_button = QPushButton(_("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Start file verification/download process
        self.start_initialization()
            
            
    def start_initialization(self):
        """Start checking and downloading the database file."""

        self.worker = DataInitializationWorker(self.download_url, self.data_file_path)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.download_completed.connect(self.on_download_completed)
        self.worker.download_failed.connect(self.on_download_failed)
        self.worker.start()

    def update_progress(self, value):
        """Update progress bar."""
        self.status_label.setText(_("Downloading database file: {progress}%").format(progress=value))
        self.progress_bar.setValue(value)

    def on_download_completed(self):
        """Handle successful download."""

        self.status_label.setText(_("Database file downloaded successfully."))
        self.accept()  # Close the dialog

    def on_download_failed(self, error_message):
        """Handle failed download."""
        self.status_label.setText(_("Download failed: {error}").format(error=error_message))
        self.cancel_button.setText(_("Close"))
        self.cancel_button.setEnabled(True)
