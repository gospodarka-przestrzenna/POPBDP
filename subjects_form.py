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



import sqlite3
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QTreeView, QVBoxLayout, QPushButton, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from .config import DB_PATH
from .utils.translations import _, gus_language
from .columnname_form import ChooseColumnName


class SubjectsForm(QDialog):
    """
    SubjectsForm is a dialog for displaying and selecting data subjects and variables.
    It uses a tree view to represent hierarchical data and allows users to select variables
    with checkboxes.
    """

    def __init__(self, variableNames):
        """
        Initializes the SubjectsForm dialog.
        
        Args:
            variableNames (dict): A dictionary to store user-defined column names for variables.
        """
        super().__init__()
        self.variableNames = variableNames
        self.selected_codes = []  # List to store selected variable codes

        # Set up the window title
        self.setWindowTitle(_("Select Subjects and Variables"))

        # Create the tree view
        self.tree_view = QTreeView()
        
        # Create the model for the tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([_("Name"), _("Description"), _("Subject ID")])

        # Set the model to the tree view
        self.tree_view.setModel(self.model)
        
        # Configure column widths
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.setColumnWidth(1, 150)
        self.tree_view.setColumnWidth(2, 150)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)  # First column stretches
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)    # Second column has fixed size
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)    # Third column has fixed size
        self.tree_view.header().setStretchLastSection(False)

        # Button to proceed to the next step
        self.button = QPushButton(_("Next"))
        self.button.clicked.connect(self.accept)
        self.button.setEnabled(False)  # Initially disabled until at least one variable is selected
        
        # Set up the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.resize(1000, 600)

        # Signals to handle interactions
        self.tree_view.expanded.connect(self.on_item_expanded)  # Load children when item is expanded
        self.model.itemChanged.connect(self.on_item_checked)    # Handle checkbox state changes

        # Load root-level data
        self.load_root_data()

    def load_root_data(self):
        """Loads the root-level subjects from the database into the tree view."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subject_code, name FROM subjects WHERE parent_id IS NULL and language = ?", (gus_language,))
            subjects = cursor.fetchall()
            
            for subject_id, subject_name in subjects:
                # Create a root-level item
                subject_item = QStandardItem(subject_name)
                subject_item.setData(subject_id)  # Store the subject ID
                subject_item.setFlags(subject_item.flags() & ~Qt.ItemIsEditable)  # Disable editing
                
                # Description and subject ID items
                description_item = QStandardItem(_("Main subject"))
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                code = QStandardItem(subject_id)
                code.setFlags(code.flags() & ~Qt.ItemIsEditable)

                # Add a dummy child for expansion
                subject_item.appendRow([QStandardItem(_("Loading...")), QStandardItem(""), QStandardItem("")])
                
                self.model.appendRow([subject_item, description_item, code])

    def on_item_expanded(self, index):
        """
        Handles item expansion events to dynamically load child elements.

        Args:
            index (QModelIndex): The index of the expanded item in the model.
        """
        item = self.model.itemFromIndex(index)
        
        if item.hasChildren() and item.child(0).text() == _("Loading..."):
            # Remove dummy item and load actual children
            item.removeRow(0)
            parent_id = item.data()
            self.load_children(item, parent_id)

    def load_children(self, parent_item, parent_id):
        """
        Loads child items for the given parent item from the database.

        Args:
            parent_item (QStandardItem): The parent item to which children will be added.
            parent_id (str): The ID of the parent item.
        """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subject_code, name FROM subjects WHERE parent_id = ? and language = ?", (parent_id,gus_language))
            children = cursor.fetchall()
            
            for subject_code, child_name in children:
                # Create a child item
                child_item = QStandardItem(child_name)
                child_item.setData(subject_code)
                child_item.setFlags(child_item.flags() & ~Qt.ItemIsEditable)
                description_item = QStandardItem(_("Subtopic"))
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                code = QStandardItem(subject_code)
                code.setFlags(code.flags() & ~Qt.ItemIsEditable)
                
                # Add a dummy child for further expansion
                child_item.appendRow([QStandardItem(_("Loading...")), QStandardItem(""), QStandardItem("")])
                parent_item.appendRow([child_item, description_item, code])

            # Load variables for the parent item
            cursor.execute("SELECT id, n1, n2, n3, n4, n5, measure_unit_name FROM variables WHERE subject_id = ? and language = ?", (parent_id,gus_language))
            variables = cursor.fetchall()
            
            for var_id, var_name1, var_name2, var_name3, var_name4, var_name5, measure_unit_name in variables:
                # Create a variable item with a checkbox
                combined_name = '\n'.join(filter(None, [var_name1, var_name2, var_name3, var_name4, var_name5]))
                var_item = QStandardItem(combined_name)
                var_item.setFlags(var_item.flags() & ~Qt.ItemIsEditable)
                var_item.setCheckable(True)
                var_item.setData(str(var_id))

                description_item = QStandardItem(measure_unit_name)
                description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
                code = QStandardItem(str(var_id))
                code.setFlags(code.flags() & ~Qt.ItemIsEditable)
                parent_item.appendRow([var_item, description_item, code])

    def on_item_checked(self, item):
        """
        Handles checkbox state changes for variables.

        Args:
            item (QStandardItem): The item whose checkbox state has changed.
        """
        if item.isCheckable():
            code = item.data()
            if item.checkState() == Qt.Checked:
                if code not in self.selected_codes:
                    form = ChooseColumnName(code, self.variableNames)
                    result = form.exec_()
                    if result == QDialog.Accepted and code in self.variableNames:
                        self.variableNames[code] = form.column_name.text()
                        self.selected_codes.append(code)
                    else:
                        item.setCheckState(Qt.Unchecked)

            else:
                if code in self.selected_codes:
                    self.selected_codes.remove(code)
                    del self.variableNames[code]


        # Enable or disable the Next button based on selections
        self.button.setEnabled(len(self.selected_codes) > 0)

    def closeEvent(self, event):
        """
        Handles the dialog close event.
        Rejects the form when the dialog is closed.
        """
        self.reject()
        event.accept()
