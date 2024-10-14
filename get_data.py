# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Wawrzyniec Zipser, Maciej Kamiński (kaminski.maciej@pwr.edu.pl) Politechnika Wrocławska
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


from PyQt5.QtWidgets import QAction, QDialog
from qgis.core import QgsProject
from .translations import _
from .config import DB_PATH
from .subjects_form import SubjectsForm
from .units_form import UnitsForm
from .years_form import YearsForm
from .datafetch_form import DataFetchForm
from .approach_form import ApproachForm

class GetData(QAction):
    """
    GetData class manages the main logic and workflow of the plugin, 
    connecting various forms and data fetching functionalities.
    """

    def __init__(self, plugin):
        """
        Initialize the GetData class, setting up the main plugin action.
        
        Parameters:
            plugin (QgsPlugin): Reference to the main plugin instance.
        """
        super(GetData, self).__init__(plugin.icon('ico1.png'), _("Fetch GUS data"), plugin.iface.mainWindow())
        self.triggered.connect(self.run)

        # Assign plugin references
        self.plugin = plugin
        self.iface = plugin.iface

        
        # Initialize data containers
        self.do_merge = False
        self.variables = [] 
        self.units = []
        self.variableNames = {}
        self.layer = None

    def run(self):
        """
        Initiates the plugin by resetting data and launching the first form.
        """
        # Clear previous session data
        self.variables.clear()
        self.units.clear()

        self.layer = None

        # Launch the first form
        self.show_approach_form()

    def show_approach_form(self):
        """
        Displays the approach selection form and connects its completion
        to the next form (subjects selection).
        """
        self.approach_form = ApproachForm()
        self.approach_form.accepted.connect(self.show_units_form)
        result = self.approach_form.exec_()
        if result == QDialog.Rejected:
            # If the dialog is closed, terminate the plugin
            return
        self.do_merge = self.approach_form.option2.isChecked()

    def show_units_form(self):
        """
        Displays the units selection form after the approach form 
        and connects its completion to the subjects form.
        """
        self.units_form = UnitsForm(self.do_merge)
        self.units_form.accepted.connect(self.show_subjects_form)
        result = self.units_form.exec_()
        if result == QDialog.Rejected:
            # If the dialog is closed, terminate the plugin
            return
        self.units = self.units_form.selected_codes

    def show_subjects_form(self):
        """
        Displays the subjects selection form and connects its completion
        to the data fetching form.
        """
        self.subjects_form = SubjectsForm(self.variableNames)
        self.subjects_form.accepted.connect(self.show_datafetch_form) 
        result = self.subjects_form.show()
        if result == QDialog.Rejected:
            # If the dialog is closed, terminate the plugin
            return
        self.variables = self.subjects_form.selected_codes
        self.variableNames = self.subjects_form.variableNames

    def show_datafetch_form(self):
        """
        Displays the data fetching form, initiates API requests, 
        and tracks progress for data retrieval.
        """        
        self.datafetch_form = DataFetchForm(
            self.do_merge,
            self.units,
            self.variables,
            self.variableNames,
        )
        self.datafetch_form.accepted.connect(self.show_years_form)
        result = self.datafetch_form.exec_()
        if result == QDialog.Rejected:
            # If the dialog is closed, terminate the plugin
            return
        
        
    def show_years_form(self):
        """
        Displays the years selection form after data fetching and 
        connects its completion to data processing.
        """

        # Get the fetched data layer from the data fetching form
        self.layer = self.datafetch_form.worker.layer

        self.years_form = YearsForm(self.layer.year_columns.keys())
        self.years_form.accepted.connect(self.process_data)
        result = self.years_form.exec_()
        if result == QDialog.Rejected:
            # If the dialog is closed, terminate the plugin
            return
        
        

    def process_data(self):
        """
        Finalizes data retrieval and processing by removing 
        unnecessary columns and adding the processed data to QGIS as a layer.
        """        
        self.layer.remove_unwanted_years_columns(self.years_form.selected_years)
        QgsProject.instance().addMapLayer(self.layer)
        