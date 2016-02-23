# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a handler for GreaseMonkey related URLs.
"""

from __future__ import unicode_literals

from ..Network.UrlInterceptor import UrlInterceptor


class GreaseMonkeyUrlInterceptor(UrlInterceptor):
    """
    Class implementing a handler for GreaseMonkey related URLs.
    """
    def __init__(self, manager):
        """
        Constructor
        
        @param manager reference to the GreaseMonkey manager
        @type GreaseMonkeyManager
        """
        super(GreaseMonkeyUrlInterceptor, self).__init__(manager)
        
        self.__manager = manager
    
    def interceptRequest(self, info):
        """
        Public method to handle a GreaseMonkey request.
        
        @param info request info object
        @type QWebEngineUrlRequestInfo
        """
        if info.requestUrl().toString.endswith(".user.js"):
            self.__manager.downloadScript(info.requestUrl())
            info.block(True)
