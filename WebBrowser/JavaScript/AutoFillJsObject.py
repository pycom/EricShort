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
        """
        # TODO: AutoFill
        pass
##void AutoFillJsObject::formSubmitted(const QString &frameUrl, const QString &username, const QString &password, const QByteArray &data)
##{
##    PageFormData formData;
##    formData.username = username;
##    formData.password = password;
##    formData.postData = data;
##
##    mApp->autoFill()->saveForm(m_jsObject->page(), QUrl(frameUrl), formData);
##}
