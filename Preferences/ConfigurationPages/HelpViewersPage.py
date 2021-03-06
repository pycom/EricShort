# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Help Viewers configuration page.
"""

from __future__ import unicode_literals

from PyQt5.QtWidgets import QButtonGroup

from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_HelpViewersPage import Ui_HelpViewersPage

import Preferences


class HelpViewersPage(ConfigurationPageBase, Ui_HelpViewersPage):
    """
    Class implementing the Help Viewers configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(HelpViewersPage, self).__init__()
        self.setupUi(self)
        self.setObjectName("HelpViewersPage")
        
        self.customViewerPicker.setMode(E5PathPickerModes.OpenFileMode)
        
        self.helpViewerGroup = QButtonGroup()
        self.helpViewerGroup.addButton(self.helpBrowserButton)
        self.helpViewerGroup.addButton(self.qtAssistantButton)
        self.helpViewerGroup.addButton(self.webBrowserButton)
        self.helpViewerGroup.addButton(self.customViewerButton)
        
        # set initial values
        hvId = Preferences.getHelp("HelpViewerType")
        # check availability of QtWebKit
        try:
            from PyQt5 import QtWebKit      # __IGNORE_WARNING__
        except ImportError:
            # not available, reset help viewer to default
            if hvId == 1:
                hvId = Preferences.Prefs.helpDefaults["HelpViewerType"]
            self.helpBrowserButton.setEnabled(False)
        
        if hvId == 1:
            self.helpBrowserButton.setChecked(True)
        elif hvId == 2:
            self.qtAssistantButton.setChecked(True)
        elif hvId == 3:
            self.webBrowserButton.setChecked(True)
        else:
            self.customViewerButton.setChecked(True)
        self.customViewerPicker.setText(
            Preferences.getHelp("CustomViewer"))
        
    def save(self):
        """
        Public slot to save the Help Viewers configuration.
        """
        if self.helpBrowserButton.isChecked():
            hvId = 1
        elif self.qtAssistantButton.isChecked():
            hvId = 2
        elif self.webBrowserButton.isChecked():
            hvId = 3
        elif self.customViewerButton.isChecked():
            hvId = 4
        Preferences.setHelp("HelpViewerType", hvId)
        Preferences.setHelp(
            "CustomViewer",
            self.customViewerPicker.text())
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = HelpViewersPage()
    return page
