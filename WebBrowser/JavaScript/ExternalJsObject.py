# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the JavaScript external object being the endpoint of
a web channel.
"""

#
# This code was ported from QupZilla and modified.
# Copyright (C) David Rosca <nowrep@gmail.com>
#

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSlot, QObject, QUrl, QByteArray

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
    
    @pyqtSlot(str)
    def AddSearchProvider(self, engineUrl):
        """
        Public slot to add a search provider.
        
        @param engineUrl engineUrl of the XML file defining the search provider
        @type str
        """
        WebBrowser.WebBrowserWindow.WebBrowserWindow.openSearchManager()\
        .addEngine(QUrl(engineUrl))
    
    @pyqtSlot(str, str, str, QByteArray)
    def formSubmitted(self, urlStr, userName, password, data):
        """
        Public slot passing form data to the password manager.
        
        @param urlStr form submission URL
        @type str
        @param userName name of the user
        @type str
        @param password user password
        @type str
        @param data data to be submitted
        @type QByteArray
        """
        import WebBrowser.WebBrowserWindow
        WebBrowser.WebBrowserWindow.WebBrowserWindow.passwordManager()\
        .formSubmitted(urlStr, userName, password, data,
                       self.page())
