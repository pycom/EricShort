# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Web Browser configuration page.
"""

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFontDialog

from E5Gui.E5PathPicker import E5PathPickerModes

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_WebBrowserAppearancePage import Ui_WebBrowserAppearancePage

import Preferences

try:
    MonospacedFontsOption = QFontDialog.MonospacedFonts
except AttributeError:
    MonospacedFontsOption = QFontDialog.FontDialogOptions(0x10)


class WebBrowserAppearancePage(ConfigurationPageBase,
                               Ui_WebBrowserAppearancePage):
    """
    Class implementing the Web Browser Appearance page.
    """
    def __init__(self):
        """
        Constructor
        """
        super(WebBrowserAppearancePage, self).__init__()
        self.setupUi(self)
        self.setObjectName("WebBrowserAppearancePage")
        
        self.styleSheetPicker.setMode(E5PathPickerModes.OpenFileMode)
        self.styleSheetPicker.setFilters(self.tr(
            "Cascading Style Sheets (*.css);;All files (*)"))
        
        self.__displayMode = None
        
        # set initial values
        self.standardFont = Preferences.getWebBrowser("StandardFont")
        self.standardFontSample.setFont(self.standardFont)
        self.standardFontSample.setText(
            "{0} {1}".format(self.standardFont.family(),
                             self.standardFont.pointSize()))
        
        self.fixedFont = Preferences.getWebBrowser("FixedFont")
        self.fixedFontSample.setFont(self.fixedFont)
        self.fixedFontSample.setText(
            "{0} {1}".format(self.fixedFont.family(),
                             self.fixedFont.pointSize()))
        
        self.initColour("SaveUrlColor", self.secureURLsColourButton,
                        Preferences.getWebBrowser)
        
        self.autoLoadImagesCheckBox.setChecked(
            Preferences.getWebBrowser("AutoLoadImages"))
        
        self.styleSheetPicker.setText(
            Preferences.getWebBrowser("UserStyleSheet"))
        
        self.tabsCloseButtonCheckBox.setChecked(
            Preferences.getUI("SingleCloseButton"))
        self.warnOnMultipleCloseCheckBox.setChecked(
            Preferences.getWebBrowser("WarnOnMultipleClose"))
    
    def setMode(self, displayMode):
        """
        Public method to perform mode dependent setups.
        
        @param displayMode mode of the configuration dialog
            (ConfigurationWidget.DefaultMode,
             ConfigurationWidget.HelpBrowserMode,
             ConfigurationWidget.TrayStarterMode)
        """
        from ..ConfigurationDialog import ConfigurationWidget
        assert displayMode in (
            ConfigurationWidget.DefaultMode,
            ConfigurationWidget.WebBrowserMode,
        )
        
        self.__displayMode = displayMode
        if self.__displayMode != ConfigurationWidget.WebBrowserMode:
            self.tabsGroupBox.hide()
    
    def save(self):
        """
        Public slot to save the Help Viewers configuration.
        """
        Preferences.setWebBrowser("StandardFont", self.standardFont)
        Preferences.setWebBrowser("FixedFont", self.fixedFont)
        
        Preferences.setWebBrowser(
            "AutoLoadImages",
            self.autoLoadImagesCheckBox.isChecked())
        
        Preferences.setWebBrowser(
            "UserStyleSheet",
            self.styleSheetPicker.text())
        
        self.saveColours(Preferences.setWebBrowser)
        
        from ..ConfigurationDialog import ConfigurationWidget
        if self.__displayMode == ConfigurationWidget.WebBrowserMode:
            Preferences.setUI(
                "SingleCloseButton",
                self.tabsCloseButtonCheckBox.isChecked())
        
        Preferences.setWebBrowser(
            "WarnOnMultipleClose",
            self.warnOnMultipleCloseCheckBox.isChecked())
    
    @pyqtSlot()
    def on_standardFontButton_clicked(self):
        """
        Private method used to select the standard font.
        """
        self.standardFont = \
            self.selectFont(self.standardFontSample, self.standardFont, True)
    
    @pyqtSlot()
    def on_fixedFontButton_clicked(self):
        """
        Private method used to select the fixed-width font.
        """
        self.fixedFont = self.selectFont(
            self.fixedFontSample, self.fixedFont, True,
            options=MonospacedFontsOption)
    

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    @return reference to the instantiated page (ConfigurationPageBase)
    """
    page = WebBrowserAppearancePage()
    return page
