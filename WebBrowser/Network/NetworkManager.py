# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a network manager class.
"""

from __future__ import unicode_literals

from PyQt5.QtWidgets import QDialog
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkProxy

from E5Gui import E5MessageBox

from E5Network.E5NetworkProxyFactory import proxyAuthenticationRequired

import Preferences


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
        
        self.proxyAuthenticationRequired.connect(
            lambda proxy, auth: self.proxyAuthentication(
                proxy.hostName(), auth))
        self.authenticationRequired.connect(
            lambda reply, auth: self.authentication(reply.url(), auth))
    
    def certificateError(self, error, view):
        """
        Public method to handle SSL certificate errors.
        
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
    
    def authentication(self, url, auth):
        """
        Public slot to handle an authentication request.
        
        @param url URL requesting authentication (QUrl)
        @param auth reference to the authenticator object (QAuthenticator)
        """
        urlRoot = "{0}://{1}"\
            .format(url.scheme(), url.authority())
        realm = auth.realm()
        if not realm and 'realm' in auth.options():
            realm = auth.option("realm")
        if realm:
            info = self.tr("<b>Enter username and password for '{0}', "
                           "realm '{1}'</b>").format(urlRoot, realm)
        else:
            info = self.tr("<b>Enter username and password for '{0}'</b>")\
                .format(urlRoot)
        
        from UI.AuthenticationDialog import AuthenticationDialog
        # TODO: Password Manager
##        import WebBrowser.WebBrowserWindow
        
        dlg = AuthenticationDialog(info, auth.user(),
                                   Preferences.getUser("SavePasswords"),
                                   Preferences.getUser("SavePasswords"))
        # TODO: Password Manager
##        if Preferences.getUser("SavePasswords"):
##            username, password = \
##                WebBrowser.WebBrowserWindow.WebBrowserWindow.passwordManager()\
##                .getLogin(url, realm)
##            if username:
##                dlg.setData(username, password)
        if dlg.exec_() == QDialog.Accepted:
            username, password = dlg.getData()
            auth.setUser(username)
            auth.setPassword(password)
            # TODO: Password Manager
##            if Preferences.getUser("SavePasswords"):
##                WebBrowser.WebBrowserWindow.WebBrowserWindow.passwordManager()\
##                .setLogin(url, realm, username, password)
    
    def proxyAuthentication(self, hostname, auth):
        """
        Public slot to handle a proxy authentication request.
        
        @param hostname name of the proxy host
        @type str
        @param auth reference to the authenticator object
        @type QAuthenticator
        """
        proxy = QNetworkProxy.applicationProxy()
        if proxy.user() and proxy.password():
            auth.setUser(proxy.user())
            auth.setPassword(proxy.password())
            return
        
        proxyAuthenticationRequired(proxy, auth)
