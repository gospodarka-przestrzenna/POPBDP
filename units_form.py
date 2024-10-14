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
from PyQt5.QtWidgets import QTreeView, QVBoxLayout, QPushButton, QHeaderView, QDialog
from PyQt5.QtCore import Qt
from .config import DB_PATH
from .utils.translations import _, gus_language
from .utils.teryt import Teryt
from .utils.expander import Expander

class UnitsForm(QDialog):
    """
    UnitsForm class provides a tree view for selecting territorial units
    with hierarchical structure and checkboxes.
    """

    def __init__(self, do_merge=False):
        """
        Initializes the UnitsForm dialog.
        
        Args:
            do_merge (bool): If True, smallest units like rural/urban communes will be merged.
        """
        super().__init__()

        self.do_merge = do_merge  # Merge flag for handling smallest units
        self.full_code_list = []  # List to store selected codes
        self.teryt = Teryt()

        # Tree view to display territorial units
        self.tree_view = QTreeView()
        
        # Model for the tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([_("Name"), _("Type"), _("Short code"), _("Full code")])
        self.tree_view.setModel(self.model)

        # Set column widths and resizing behavior
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.setColumnWidth(1, 150)
        self.tree_view.setColumnWidth(2, 100)
        self.tree_view.setColumnWidth(3, 150)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.Fixed)
        self.tree_view.header().setStretchLastSection(False)

        # "Next" button to proceed to the next step
        self.button = QPushButton(_("Next"))
        self.button.clicked.connect(self.accept)
        self.button.setEnabled(False)  # Initially disabled until units are selected
        
        # Main layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.setWindowTitle(_("Choose territorial units"))
        self.resize(800, 500)

        # Signals to handle interactions
        self.tree_view.expanded.connect(self.on_item_expanded)  # Load children when a parent is expanded
        self.model.itemChanged.connect(self.on_item_changed)   # Handle checkbox state changes

        # Load root data (voivodeships and subregions)
        self.load_root_data()

    def load_root_data(self):
        """
        Loads voivodeships (level 2) and their subregions (level 4) into the tree view.
        """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Fetch voivodeships (level 2) 
            cursor.execute("SELECT full_code, short_code, name, kind, level FROM teryt_codes WHERE level = 2 and language = ?", (gus_language,))
            regions = cursor.fetchall()

            # Fetch subregions (level 4)
            cursor.execute("SELECT full_code, short_code, name, kind, level FROM teryt_codes WHERE level = 4 and language = ?", (gus_language,))
            subregions = cursor.fetchall()

            for full_code, short_code, name, kind, level in regions:
                # Create voivodeship items
                region_item = QStandardItem(name)
                region_item.setData(full_code)
                region_item.setFlags(region_item.flags() & ~Qt.ItemIsEditable)

                type_item = QStandardItem(_("Voivodeship"))
                type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)

                short_code_item = QStandardItem(short_code)
                short_code_item.setFlags(short_code_item.flags() & ~Qt.ItemIsEditable)

                full_code_item = QStandardItem(full_code)
                full_code_item.setFlags(full_code_item.flags() & ~Qt.ItemIsEditable)

                # Add subregions for the voivodeship
                for sub_full_code, sub_short_code, sub_name, sub_kind, sub_level in subregions:
                    if sub_full_code.startswith(full_code[:4]):
                        subregion_item = QStandardItem(sub_name)
                        subregion_item.setData(sub_full_code)
                        subregion_item.setFlags(subregion_item.flags() & ~Qt.ItemIsEditable)
                        subregion_item.setCheckable(True)  # Checkbox for subregions

                        sub_type_item = QStandardItem(_("Subregion"))
                        sub_type_item.setFlags(sub_type_item.flags() & ~Qt.ItemIsEditable)

                        sub_short_code_item = QStandardItem(sub_short_code)
                        sub_short_code_item.setFlags(sub_short_code_item.flags() & ~Qt.ItemIsEditable)

                        sub_full_code_item = QStandardItem(sub_full_code)
                        sub_full_code_item.setFlags(sub_full_code_item.flags() & ~Qt.ItemIsEditable)

                        # Add dummy item for further expansion
                        subregion_item.appendRow([QStandardItem(_("Loading...")), QStandardItem(""), QStandardItem(""), QStandardItem("")])

                        region_item.appendRow([subregion_item, sub_type_item, sub_short_code_item, sub_full_code_item])

                # Add voivodeship to the model
                self.model.appendRow([region_item, type_item, short_code_item, full_code_item])

    def on_item_expanded(self, index):
        """
        Loads children of an expanded item (counties and communes).
        
        Args:
            index (QModelIndex): Index of the expanded item in the tree view.
        """
        item = self.model.itemFromIndex(index)
        if item.hasChildren() and item.child(0).text() == _("Loading..."):
            item.removeRow(0)  # Remove dummy item
            parent_full_code = item.data()
            self.load_children(item, parent_full_code)
            # when item is seelected its children must be checked
            if item.checkState() == Qt.Checked:
                self.check_children(item)
    
    def load_children(self, item, full_code):
        """
        Loads children of a given parent item (counties and communes).
        
        Args:
            item (QStandardItem): The parent item in the tree view.
            full_code (str): The full code of the parent item.
        """

        childrens = Expander().expand_code(full_code)
        if childrens is None:
            return
        for full_code, name, kind, level in childrens:
            
            type_name = Teryt().get_type_name(level, kind)
            short_code = full_code[2:4] + full_code[7:11]

            child_item = QStandardItem(name)
            child_item.setData(full_code)
            child_item.setFlags(child_item.flags() & ~Qt.ItemIsEditable)
            child_item.setCheckable(True)
            
            type_item = QStandardItem(type_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)

            short_code_item = QStandardItem(short_code)
            short_code_item.setFlags(short_code_item.flags() & ~Qt.ItemIsEditable)

            full_code_item = QStandardItem(full_code)
            full_code_item.setFlags(full_code_item.flags() & ~Qt.ItemIsEditable)

            
            if Expander().expandable(full_code, self.do_merge):
                child_item.appendRow([QStandardItem(_("Loading...")), QStandardItem(""), QStandardItem(""), QStandardItem("")])

            item.appendRow([child_item, type_item, short_code_item, full_code_item])

    def check_children(self,item):
        """
        Checks all children of an item. (marks checkbox as checked)

        Args:
            item (QStandardItem): The item whose children will be checked.
        """
        for row in range(item.rowCount()):
            child = item.child(row)
            if child.isCheckable():
                if item.checkState() == Qt.Checked:
                    if child.data() in self.full_code_list:
                        self.full_code_list.remove(child.data())
                child.setFlags(child.flags() & ~Qt.ItemIsEnabled)
                child.setCheckState(Qt.Checked)
                self.check_children(child)

    def uncheck_children(self,item):
        """
        Unchecks all children of an item.
        
        Args:
            item (QStandardItem): The item whose children will be unchecked.
        """
        for row in range(item.rowCount()):
            child = item.child(row)
            if child.isCheckable():
                if item.checkState() == Qt.Unchecked:
                    if child.data() in self.full_code_list:
                        self.full_code_list.remove(child.data())
                child.setCheckState(Qt.Unchecked)
                child.setFlags(child.flags() | Qt.ItemIsEnabled)
                self.uncheck_children(child)

    def on_item_changed(self, item: QStandardItem):
        """
        Updates the selected codes list when a checkbox state changes. Just flip the state of the children
        
        Args:
            item (QStandardItem): The item whose checkbox state changed.
        """

        if item.isCheckable() and item.isEnabled():
            full_code = item.data()
            if item.checkState() == Qt.Checked:
                self.check_children(item)
                if full_code not in self.full_code_list:
                    self.full_code_list.append(full_code)
            else:
                self.uncheck_children(item)
                if full_code in self.full_code_list:
                    self.full_code_list.remove(full_code)

        self.button.setEnabled(len(self.full_code_list) > 0)

    def closeEvent(self, event):
        """
        Handles the dialog close event. If the user closes the dialog window, the form is rejected.
        """
        event.accept()
        self.reject()
