# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a network manager class.
"""

from PyQt5.QtNetwork import QNetworkAccessManager

from E5Gui import E5MessageBox


class NetworkManager(QNetworkAccessManager):
    """
    Class implementing a network manager.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        super(NetworkManager, self).__init__(parent)
        
        self.__ignoredSslErrors = {}
        # dictionary of temporarily ignore SSL errors
        
        # TODO: Proxy Authentication
##        self.proxyAuthenticationRequired.connect(proxyAuthenticationRequired)
        # TODO: Authentication
##        self.authenticationRequired.connect(self.authenticationRequired)
    
    def certificateError(self, error, view):
        """
        Protected method to handle SSL certificate errors.
        
        @param error object containing the certificate error information
        @type QWebEngineCertificateError
        @param view reference to a view to be used as parent for the dialog
        @type QWidget
        @return flag indicating to ignore this error
        @rtype bool
        """
        # TODO: permanent SSL certificate error exceptions
        host = error.url().host()
        
        if host in self.__ignoredSslErrors and \
                self.__ignoredSslErrors[host] == error.error():
            return True
        
        title = self.tr("SSL Certificate Error")
        accept = E5MessageBox.yesNo(
            view,
            title,
            self.tr("""<b>{0}</b>"""
                    """<p>The page you are trying to access has errors"""
                    """ in the SSL certificate.</p>"""
                    """<ul><li>{1}</li></ul>"""
                    """<p>Would you like to make an exception?</p>""")
            .format(title, error.errorDescription()),
            icon=E5MessageBox.Warning)
        if accept:
            self.__ignoredSslErrors[error.url().host()] = error.error()
            return True
        
        return False
