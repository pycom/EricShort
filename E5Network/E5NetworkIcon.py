# -*- coding: utf-8 -*-

# Copyright (c) 2015 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a statusbar icon tracking the network status.
"""

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtNetwork import QNetworkConfigurationManager

from E5Gui.E5ClickableLabel import E5ClickableLabel

import UI.PixmapCache


class E5NetworkIcon(E5ClickableLabel):
    """
    Class implementing a statusbar icon tracking the network status.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(E5NetworkIcon, self).__init__(parent)
        
        self.__networkManager = QNetworkConfigurationManager(self)
        self.__onlineStateChanged(self.__networkManager.isOnline())
        
        self.__networkManager.onlineStateChanged.connect(
            self.__onlineStateChanged)
    
    @pyqtSlot(bool)
    def __onlineStateChanged(self, online):
        """
        Private slot handling online state changes.
        
        @param online flag indicating the online status
        @type bool
        """
        if online:
            self.setPixmap(UI.PixmapCache.getPixmap("network-online.png"))
        else:
            self.setPixmap(UI.PixmapCache.getPixmap("network-offline.png"))
        
        tooltip = self.tr("<p>Shows the network status<br/><br/>"
                         "<b>Network:</b> {0}</p>")
        
        if self.__networkManager.isOnline():
            tooltip = tooltip.format(self.tr("Connected"))
        else:
            tooltip = tooltip.format(self.tr("Offline"))
        
        self.setToolTip(tooltip)
    
    def isOnline(self):
        """
        Public method to get the online state.
        
        @return online state
        @rtype bool
        """
        return self.__networkManager.isOnline()
