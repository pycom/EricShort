# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the JavaScript external object being the endpoint of
a web channel.
"""

#
# This code was ported from QupZilla.
# Copyright (C) David Rosca <nowrep@gmail.com>
#

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSlot, QObject, QUrl

from .AutoFillJsObject import AutoFillJsObject

import WebBrowser.WebBrowserWindow


class ExternalJsObject(QObject):
    """
    Class implementing the endpoint of our web channel.
    """
    def __init__(self, page):
        """
        Constructor
        
        @param page reference to the web page object
        @type WebBrowserPage
        """
        super(ExternalJsObject, self).__init__(page)
        
        self.__page = page
        self.__autoFill = AutoFillJsObject(self)
    
    def page(self):
        """
        Public method returning a reference to the web page object.
        
        @return reference to the web page object
        @rtype WebBrowserPage
        """
        return self.__page
    
    @pyqtSlot(result=QObject)
    def speedDial(self):
        """
        Public method returning a reference to a speed dial object.
        
        @return reference to a speed dial object
        @rtype SpeedDial
        """
        if self.__page.url().toString() != "eric:speeddial":
            return None
        
        # TODO: SpeedDial
##        return WebBrowser.WebBrowserWindow.WebBrowserWindow.speedDial()
        return None
    
    @pyqtSlot(result=QObject)
    def autoFill(self):
        """
        Public method returning a reference to the auto fill object.
        
        @return reference to the auto fill object
        @rtype AutoFillJsObject
        """
        return self.__autoFill
    
    @pyqtSlot(str)
    def AddSearchProvider(self, engineUrl):
        """
        Public slot to add a search provider.
        
        @param engineUrl engineUrl of the XML file defining the search provider
        @type str
        """
        WebBrowser.WebBrowserWindow.WebBrowserWindow.openSearchManager()\
        .addEngine(QUrl(engineUrl))
##
##int ExternalJsObject::IsSearchProviderInstalled(const QString &engineURL)
##{ Slot
##    qDebug() << "NOT IMPLEMENTED: IsSearchProviderInstalled()" << engineURL;
##    return 0;
##}
