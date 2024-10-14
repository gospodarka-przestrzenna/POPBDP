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
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from datetime import datetime
from .utils.translations import _

class YearsForm(QDialog):
    """
    Dialog for selecting years from a predefined list with checkboxes.
    Allows the user to select multiple years and validates the selection.
    """
    def __init__(self, years):
        """
        Initializes the dialog.

        Args:
            years (list): List of available years for selection.
        """
        super().__init__()
        self.years = years  # List of all available years
        self.selected_years = []  # List of selected years

        # Main window settings
        self.setWindowTitle(_("Select Years"))
        self.resize(400, 300)

        # List widget for displaying years with checkboxes
        self.year_list = QListWidget()

        # "Next" button to proceed
        self.next_button = QPushButton(_("Add Layer to Map"))
        self.next_button.setEnabled(False)  # Initially disabled until a year is selected
        self.next_button.clicked.connect(self.accept)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.year_list)
        layout.addWidget(self.next_button)
        self.setLayout(layout)

        # Signal to detect checkbox state changes
        self.year_list.itemChanged.connect(self.on_item_changed)

    def populate_years(self):
        """
        Populates the list widget with years as checkable items.
        Automatically checks the year preceding the current year.
        """
        current_year = datetime.now().year
        years = sorted(self.years, reverse=True)  # Sort years in descending order

        for year in years:
            # Create a list item with a checkbox
            item = QListWidgetItem(str(year))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkboxes
            item.setCheckState(Qt.Checked if int(year) == int(current_year) - 1 else Qt.Unchecked)  # Check the previous year by default
            self.year_list.addItem(item)

            # Add pre-checked years to the selected list
            if item.checkState() == Qt.Checked:
                self.selected_years.append(year)

        # Enable the "Next" button if at least one year is selected
        self.update_next_button_state()

    def showEvent(self, event):
        """
        Triggered when the dialog is shown.
        Ensures the year list is populated.
        """
        self.populate_years()

    def on_item_changed(self, item):
        """
        Updates the list of selected years when a checkbox is checked or unchecked.

        Args:
            item (QListWidgetItem): The item whose checkbox state changed.
        """
        year = str(item.text())

        if item.checkState() == Qt.Checked:
            if year not in self.selected_years:
                self.selected_years.append(year)
        else:
            if year in self.selected_years:
                self.selected_years.remove(year)

        # Update the state of the "Next" button
        self.update_next_button_state()

    def update_next_button_state(self):
        """
        Enables or disables the "Next" button based on whether any years are selected.
        """
        self.next_button.setEnabled(len(self.selected_years) > 0)

    def closeEvent(self, event):
        """
        Handles the close event for the dialog.

        Args:
            event (QCloseEvent): The close event object.
        """
        self.reject()  # Reject the dialog
        event.accept()
