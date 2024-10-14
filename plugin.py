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

from os import path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from .get_data import GetBDLData

class QuickBDL(object):
    def __init__(self,iface):
        self.iface=iface
        self.plugin_path=path.dirname(path.abspath(__file__))
        self.plugin_menu_entry="&QuickBDL"
        self.menu_actions=[]
        #adding actions
        # Here add actions 
        self.menu_actions.append(GetBDLData(self))


    def initGui(self):
        """
        Gui initialization and actions adding
        """
        for action in self.menu_actions:
            self.iface.addPluginToMenu(self.plugin_menu_entry,action)
            self.iface.addToolBarIcon(action)

    def unload(self):
        """
        Gui purge
        """
        for action in self.menu_actions:
            self.iface.removePluginMenu(self.plugin_menu_entry,action)
            self.iface.removeToolBarIcon(action)

    def ui_loader(self,*ui_name):
        """
        Returns object created based on provided .ui filename.
        In addition subdirectory can be stated:
        ui_loader('form.ui')
        ui_loader('formsdir','form.ui')
        """
        return uic.loadUi(path.join(self.plugin_path,*ui_name))

    def icon(self,name):
        icon_path=path.join(self.plugin_path,'images',name)
        return QIcon(icon_path)
