# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a page load request object.
"""

#
# This code was ported from QupZilla.
# Copyright (C) David Rosca <nowrep@gmail.com>
#

from __future__ import unicode_literals

try:
    from enum import Enum
except ImportError:
    from ThirdParty.enum import Enum

from PyQt5.QtCore import QByteArray, QUrl


class LoadRequestOperations(Enum):
    """
    Class implementing the load request operations.
    """
    GetOperation = 0
    PostOperation = 1


class LoadRequest(object):
    """
    Class implementing a page load request object.
    """
    def __init__(self, urlOrRequest=None,
                 op=LoadRequestOperations.GetOperation, data=QByteArray()):
        """
        Constructor
        
        @param urlOrRequest URL or request object
        @type QUrl or LoadRequest
        @param op request operation
        @type LoadRequestOperations
        @param data request data
        @type QByteArray
        """
        self.__url = QUrl()
        self.__operation = op
        self.__data = QByteArray(data)
        
        if isinstance(urlOrRequest, QUrl):
            self.__url = QUrl(urlOrRequest)
        elif isinstance(urlOrRequest, LoadRequest):
            self.__url = urlOrRequest.url()
            self.__operation = urlOrRequest.operation()
            self.__data = urlOrRequest.data()
    
    def isEmpty(self):
        """
        Public method to test for an empty request.
        
        @return flag indicating an empty request
        @rtype bool
        """
        return self.__url.isEmpty()
    
    def url(self):
        """
        Public method to get the request URL.
        
        @return request URL
        @rtype QUrl
        """
        return QUrl(self.__url)
    
    def setUrl(self, url):
        """
        Public method to set the request URL.
        
        @param url request URL
        @type QUrl
        """
        self.__url = QUrl(url)
    
    def urlString(self):
        """
        Public method to get the request URL as a string.
        
        @return request URL as a string
        @rtype str
        """
        return QUrl.fromPercentEncoding(self.__url.toEncoded())
    
    def operation(self):
        """
        Public method to get the request operation.
        
        @return request operation
        @rtype one of LoadRequest.GetOperation, LoadRequest.PostOperation
        """
        return self.__operation
    
    def setOperation(self, op):
        """
        Public method to set the request operation.
        
        @param op request operation
        @type one of LoadRequest.GetOperation, LoadRequest.PostOperation
        """
        assert op in [LoadRequestOperations.GetOperation,
                      LoadRequestOperations.PostOperation]
        
        self.__operation = op
    
    def data(self):
        """
        Public method to get the request data.
        
        @return request data
        @rtype QByteArray
        """
        return QByteArray(self.__data)
    
    def setData(self, data):
        """
        Public method to set the request data
        
        @param data request data
        @type QByteArray
        """
        self.__data = QByteArray(data)
