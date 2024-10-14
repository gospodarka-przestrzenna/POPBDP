# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Wawrzyniec Zipser, Maciej Kamiński (maciej.kaminski@pwr.edu.pl) Politechnika Wrocławska
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################
__author__ = 'Wawrzyniec Zipser, Maciej Kamiński Politechnika Wrocławska'

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QButtonGroup,
    QRadioButton, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from .translations import _


class ApproachForm(QDialog):
    """
    ApproachForm is a dialog that allows the user to select data granularity.
    It provides two radio button options for granularity levels and a button to proceed.
    """

    def __init__(self):
        """
        Initialize the ApproachForm dialog.
        Sets up the UI elements and layouts.
        """
        super().__init__()

        # Set up the dialog properties
        self.setWindowTitle(_("Choose data granularity"))
        self.resize(600, 200)

        # Label to display instructions
        self.instruction_label = QLabel(_("Choose one of the following options to proceed:"))
        self.instruction_label.setAlignment(Qt.AlignCenter)

        # Radio button for the first granularity option
        # PL: "Interesują mnie dane dla drobnego podziału (W najdrobniejszym podziale są obszary wiejskie i miasta)"
        self.option1 = QRadioButton(_("I am interested in data for the smallest division (In the finest division there are rural and urban areas)"))

        # Radio button for the second granularity option
        # PL: "Interesują mnie dane historyczne (W najdrobniejszym podziale są gminy wiejsko-miejskie)"
        self.option2 = QRadioButton(_("I am interested in historical data (In the finest division there are rural-urban communes)"))

        # Button group for radio buttons to allow only one selection at a time
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.option1)
        self.radio_group.addButton(self.option2)
        
        # Next button to proceed to the next step
        self.button = QPushButton(_("Next"))
        self.button.setEnabled(False)  # Disabled until an option is selected
        self.button.clicked.connect(self.accept)

        # Connect the radio button group to enable the button when an option is selected
        self.radio_group.buttonClicked.connect(self.activate_button)

        # Main layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(self.instruction_label)  # Add instruction label to the layout
        layout.addStretch()  # Add flexible space
        layout.addWidget(self.option1)  # Add the first radio button
        layout.addWidget(self.option2)  # Add the second radio button
        layout.addStretch()  # Add more flexible space
        layout.addWidget(self.button)  # Add the Next button

        # Set the main layout
        self.setLayout(layout)

    def closeEvent(self, event):
        """
        Handles the close event for the dialog.
        If the user closes the dialog window, the form is rejected.
        """
        event.accept()    
        self.reject()
        
    def activate_button(self):
        """
        Enables the Next button when a radio button is selected.
        """
        self.button.setEnabled(True)
