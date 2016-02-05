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

from PyQt5.QtCore import QObject

from .AutoFillJsObject import AutoFillJsObject


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
    
    def autoFill(self):
        """
        Public method returning a reference to the auto fill object.
        
        @return reference to the auto fill object
        @rtype AutoFillJsObject
        """
        return self.__autoFill
    
##void ExternalJsObject::AddSearchProvider(const QString &engineUrl)
##{ Slot
##    mApp->searchEnginesManager()->addEngine(QUrl(engineUrl));
##}
##
##int ExternalJsObject::IsSearchProviderInstalled(const QString &engineURL)
##{ Slot
##    qDebug() << "NOT IMPLEMENTED: IsSearchProviderInstalled()" << engineURL;
##    return 0;
##}
