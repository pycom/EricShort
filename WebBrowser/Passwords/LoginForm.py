# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a data structure for login forms.
"""

from __future__ import unicode_literals

from PyQt5.QtCore import QUrl, QByteArray


class LoginForm(object):
    """
    Class implementing a data structure for login forms.
    """
    def __init__(self):
        """
        Constructor
        """
        self.url = QUrl()
        self.name = ""
        self.postData = QByteArray()
    
    def isValid(self):
        """
        Public method to test for validity.
        
        @return flag indicating a valid form (boolean)
        """
        return not self.url.isEmpty() and \
            not self.postData.isEmpty()
