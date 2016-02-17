# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Auto Fill web channel endpoint.
"""

#
# This code was ported from QupZilla.
# Copyright (C) David Rosca <nowrep@gmail.com>
#

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSlot, QObject, QByteArray


class AutoFillJsObject(QObject):
    """
    Class implementing the Auto Fill web channel endpoint.
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent reference to the parent object
        @type ExternalJsObject
        """
        super(AutoFillJsObject, self).__init__(parent)
        
        self.__jsObject = parent
    
    @pyqtSlot(str, str, str, QByteArray)
    def formSubmitted(self, urlStr, userName, password, data):
        """
        Public slot passing form data to the auto fill manager.
        
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
                       self.__jsObject.page())
