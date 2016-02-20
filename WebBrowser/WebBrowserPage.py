# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing the helpbrowser using QWebView.
"""

from __future__ import unicode_literals
try:
    str = unicode       # __IGNORE_EXCEPTION__
except NameError:
    pass

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QT_TRANSLATE_NOOP, \
    QUrl, QBuffer, QIODevice, QFileInfo, Qt, QTimer, QEvent, \
    QRect, QFile, QPoint, QByteArray, QEventLoop, qVersion
from PyQt5.QtGui import QDesktopServices, QClipboard, QMouseEvent, QColor, \
    QPalette
from PyQt5.QtWidgets import qApp, QStyle, QMenu, QApplication, QInputDialog, \
    QLineEdit, QLabel, QToolTip, QFrame, QDialog
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest
import sip

from E5Gui import E5MessageBox, E5FileDialog

import WebBrowser
import WebBrowser.WebBrowserWindow

from .JavaScript.ExternalJsObject import ExternalJsObject

from .Tools.WebHitTestResult import WebHitTestResult
from .Tools import Scripts

import Preferences
import UI.PixmapCache
import Globals

try:
    from PyQt5.QtNetwork import QSslCertificate
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False

# TODO: ExternalJsObject: move this to the object
###############################################################################
##
##
##class JavaScriptEricObject(QObject):
##    """
##    Class implementing an external javascript object to search via the
##    startpage.
##    """
##    # these must be in line with the strings used by the javascript part of
##    # the start page
##    translations = [
##        QT_TRANSLATE_NOOP("JavaScriptEricObject",
##                          "Welcome to eric6 Web Browser!"),
##        QT_TRANSLATE_NOOP("JavaScriptEricObject", "eric6 Web Browser"),
##        QT_TRANSLATE_NOOP("JavaScriptEricObject", "Search!"),
##        QT_TRANSLATE_NOOP("JavaScriptEricObject", "About eric6"),
##    ]
##    
##    def __init__(self, mw, parent=None):
##        """
##        Constructor
##        
##        @param mw reference to the main window 8HelpWindow)
##        @param parent reference to the parent object (QObject)
##        """
##        super(JavaScriptEricObject, self).__init__(parent)
##        
##        self.__mw = mw
##    
##    @pyqtSlot(str, result=str)
##    def translate(self, trans):
##        """
##        Public method to translate the given string.
##        
##        @param trans string to be translated (string)
##        @return translation (string)
##        """
##        if trans == "QT_LAYOUT_DIRECTION":
##            # special handling to detect layout direction
##            if qApp.isLeftToRight():
##                return "LTR"
##            else:
##                return "RTL"
##        
##        return self.tr(trans)
##    
##    @pyqtSlot(result=str)
##    def providerString(self):
##        """
##        Public method to get a string for the search provider.
##        
##        @return string for the search provider (string)
##        """
##        return self.tr("Search results provided by {0}")\
##            .format(self.__mw.openSearchManager().currentEngineName())
##    
##    @pyqtSlot(str, result=str)
##    def searchUrl(self, searchStr):
##        """
##        Public method to get the search URL for the given search term.
##        
##        @param searchStr search term (string)
##        @return search URL (string)
##        """
##        return bytes(
##            self.__mw.openSearchManager().currentEngine()
##            .searchUrl(searchStr).toEncoded()).decode()
##
###############################################################################


class WebBrowserPage(QWebEnginePage):
    """
    Class implementing an enhanced web page.
    """
##    _webPluginFactory = None
##    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this window (QWidget)
        """
        super(WebBrowserPage, self).__init__(parent)
        
        self.__setupWebChannel()
        
##        self.setPluginFactory(self.webPluginFactory())
##        
##        self.__lastRequest = None
##        self.__lastRequestType = QWebPage.NavigationTypeOther
##        
##        import WebBrowser.WebBrowserWindow
##        from .Network.NetworkAccessManagerProxy import \
##            NetworkAccessManagerProxy
##        self.__proxy = NetworkAccessManagerProxy(self)
##        self.__proxy.setWebPage(self)
##        self.__proxy.setPrimaryNetworkAccessManager(
##            WebBrowser.WebBrowserWindow.WebBrowserWindow.networkAccessManager())
##        self.setNetworkAccessManager(self.__proxy)
        
        self.__sslConfiguration = None
##        self.__proxy.finished.connect(self.__managerFinished)
##        
        self.__adBlockedEntries = []
        self.loadStarted.connect(self.__loadStarted)
##        
##        self.saveFrameStateRequested.connect(
##            self.__saveFrameStateRequested)
##        self.restoreFrameStateRequested.connect(
##            self.__restoreFrameStateRequested)
        self.featurePermissionRequested.connect(
            self.__featurePermissionRequested)
        
        self.authenticationRequired.connect(
            WebBrowser.WebBrowserWindow.WebBrowserWindow.networkManager()
            .authentication)
    
    def acceptNavigationRequest(self, url, type_, isMainFrame):
        """
        Public method to determine, if a request may be accepted.
        
        @param url URL to navigate to
        @type QUrl
        @param type_ type of the navigation request
        @type QWebEnginePage.NavigationType
        @param isMainFrame flag indicating, that the request originated from
            the main frame
        @type bool
        @return flag indicating acceptance
        @rtype bool
        """
##        self.__lastRequest = request
##        if self.__lastRequest.url() != request.url() or \
##           type_ != QWebPage.NavigationTypeOther:
##            self.__lastRequestType = type_
        
        # TODO: Qt 5.6: move to handleUnknownProtocol
        scheme = url.scheme()
        if scheme == "mailto":
            QDesktopServices.openUrl(url)
            return False
        
        # AdBlock
        if url.scheme() == "abp":
            if WebBrowser.WebBrowserWindow.WebBrowserWindow.adBlockManager()\
                    .addSubscriptionFromUrl(url):
                return False
##        
##        if type_ == QWebPage.NavigationTypeFormResubmitted:
##            res = E5MessageBox.yesNo(
##                self.view(),
##                self.tr("Resending POST request"),
##                self.tr(
##                    """In order to display the site, the request along with"""
##                    """ all the data must be sent once again, which may lead"""
##                    """ to some unexpected behaviour of the site e.g. the"""
##                    """ same action might be performed once again. Do you"""
##                    """ want to continue anyway?"""),
##                icon=E5MessageBox.Warning)
##            if not res:
##                return False
        
        return QWebEnginePage.acceptNavigationRequest(self, url, type_,
                                                      isMainFrame)
##    
##    def populateNetworkRequest(self, request):
##        """
##        Public method to add data to a network request.
##        
##        @param request reference to the network request object
##            (QNetworkRequest)
##        """
##        try:
##            request.setAttribute(QNetworkRequest.User + 100, self)
##            if self.__lastRequest.url() == request.url():
##                request.setAttribute(QNetworkRequest.User + 101,
##                                     self.__lastRequestType)
##                if self.__lastRequestType == \
##                        QWebPage.NavigationTypeLinkClicked:
##                    request.setRawHeader(b"X-Eric6-UserLoadAction",
##                                         QByteArray(b"1"))
##        except TypeError:
##            pass
##    
##    def pageAttributeId(self):
##        """
##        Public method to get the attribute id of the page attribute.
##        
##        @return attribute id of the page attribute (integer)
##        """
##        return QNetworkRequest.User + 100
##    
##    def supportsExtension(self, extension):
##        """
##        Public method to check the support for an extension.
##        
##        @param extension extension to test for (QWebPage.Extension)
##        @return flag indicating the support of extension (boolean)
##        """
##        try:
##            if extension in [QWebPage.ErrorPageExtension,
##                             QWebPage.ChooseMultipleFilesExtension]:
##                return True
##        except AttributeError:
##            pass
##        
##        return QWebPage.supportsExtension(self, extension)
##    
##    def extension(self, extension, option, output):
##        """
##        Public method to implement a specific extension.
##        
##        @param extension extension to be executed (QWebPage.Extension)
##        @param option provides input to the extension
##            (QWebPage.ExtensionOption)
##        @param output stores the output results (QWebPage.ExtensionReturn)
##        @return flag indicating a successful call of the extension (boolean)
##        """
##        if extension == QWebPage.ChooseMultipleFilesExtension:
##            info = sip.cast(option,
##                            QWebPage.ChooseMultipleFilesExtensionOption)
##            files = sip.cast(output,
##                             QWebPage.ChooseMultipleFilesExtensionReturn)
##            if info is None or files is None:
##                return super(HelpWebPage, self).extension(
##                    extension, option, output)
##            
##            suggestedFileName = ""
##            if info.suggestedFileNames:
##                suggestedFileName = info.suggestedFileNames[0]
##            
##            files.fileNames = E5FileDialog.getOpenFileNames(
##                None,
##                self.tr("Select files to upload..."),
##                suggestedFileName)
##            return True
##        
##        if extension == QWebPage.ErrorPageExtension:
##            info = sip.cast(option, QWebPage.ErrorPageExtensionOption)
##            
##            errorPage = sip.cast(output, QWebPage.ErrorPageExtensionReturn)
##            urlString = bytes(info.url.toEncoded()).decode()
##            errorPage.baseUrl = info.url
##            if info.domain == QWebPage.QtNetwork and \
##               info.error == QNetworkReply.ProtocolUnknownError:
##                url = QUrl(info.url)
##                res = E5MessageBox.yesNo(
##                    None,
##                    self.tr("Protocol Error"),
##                    self.tr("""Open external application for {0}-link?\n"""
##                            """URL: {1}""").format(
##                        url.scheme(), url.toString(
##                            QUrl.PrettyDecoded | QUrl.RemovePassword)),
##                    yesDefault=True)
##                
##                if res:
##                    QDesktopServices.openUrl(url)
##                return True
##            elif info.domain == QWebPage.QtNetwork and \
##                info.error == QNetworkReply.ContentAccessDenied and \
##                    info.errorString.startswith("AdBlockRule:"):
##                if info.frame != info.frame.page().mainFrame():
##                    # content in <iframe>
##                    docElement = info.frame.page().mainFrame()\
##                        .documentElement()
##                    for element in docElement.findAll("iframe"):
##                        src = element.attribute("src")
##                        if src in info.url.toString():
##                            element.setAttribute("style", "display:none;")
##                    return False
##                else:
##                    # the whole page is blocked
##                    rule = info.errorString.replace("AdBlockRule:", "")
##                    title = self.tr("Content blocked by AdBlock Plus")
##                    message = self.tr(
##                        "Blocked by rule: <i>{0}</i>").format(rule)
##                    
##                    htmlFile = QFile(":/html/adblockPage.html")
##                    htmlFile.open(QFile.ReadOnly)
##                    html = htmlFile.readAll()
##                    html = html.replace(
##                        "@FAVICON@", "qrc:icons/adBlockPlus16.png")
##                    html = html.replace(
##                        "@IMAGE@", "qrc:icons/adBlockPlus64.png")
##                    html = html.replace("@TITLE@", title.encode("utf8"))
##                    html = html.replace("@MESSAGE@", message.encode("utf8"))
##                    errorPage.content = html
##                    return True
##            
##            if info.domain == QWebPage.QtNetwork and \
##               info.error == QNetworkReply.OperationCanceledError and \
##               info.errorString == "eric6:No Error":
##                return False
##            
##            if info.domain == QWebPage.WebKit and info.error == 203:
##                # "Loading is handled by the media engine"
##                return False
##            
##            title = self.tr("Error loading page: {0}").format(urlString)
##            htmlFile = QFile(":/html/notFoundPage.html")
##            htmlFile.open(QFile.ReadOnly)
##            html = htmlFile.readAll()
##            pixmap = qApp.style()\
##                .standardIcon(QStyle.SP_MessageBoxWarning).pixmap(48, 48)
##            imageBuffer = QBuffer()
##            imageBuffer.open(QIODevice.ReadWrite)
##            if pixmap.save(imageBuffer, "PNG"):
##                html = html.replace("@IMAGE@", imageBuffer.buffer().toBase64())
##            pixmap = qApp.style()\
##                .standardIcon(QStyle.SP_MessageBoxWarning).pixmap(16, 16)
##            imageBuffer = QBuffer()
##            imageBuffer.open(QIODevice.ReadWrite)
##            if pixmap.save(imageBuffer, "PNG"):
##                html = html.replace(
##                    "@FAVICON@", imageBuffer.buffer().toBase64())
##            html = html.replace("@TITLE@", title.encode("utf8"))
##            html = html.replace("@H1@", info.errorString.encode("utf8"))
##            html = html.replace(
##                "@H2@", self.tr("When connecting to: {0}.")
##                .format(urlString).encode("utf8"))
##            html = html.replace(
##                "@LI-1@",
##                self.tr("Check the address for errors such as "
##                        "<b>ww</b>.example.org instead of "
##                        "<b>www</b>.example.org").encode("utf8"))
##            html = html.replace(
##                "@LI-2@",
##                self.tr(
##                    "If the address is correct, try checking the network "
##                    "connection.").encode("utf8"))
##            html = html.replace(
##                "@LI-3@",
##                self.tr(
##                    "If your computer or network is protected by a firewall "
##                    "or proxy, make sure that the browser is permitted to "
##                    "access the network.").encode("utf8"))
##            html = html.replace(
##                "@LI-4@",
##                self.tr("If your cache policy is set to offline browsing,"
##                        "only pages in the local cache are available.")
##                .encode("utf8"))
##            html = html.replace(
##                "@BUTTON@", self.tr("Try Again").encode("utf8"))
##            errorPage.content = html
##            return True
##        
##        return QWebPage.extension(self, extension, option, output)
    
    def __loadStarted(self):
        """
        Private slot to handle the loadStarted signal.
        """
        self.__adBlockedEntries = []
##    
##    def addAdBlockRule(self, rule, url):
##        """
##        Public slot to add an AdBlock rule to the page.
##        
##        @param rule AdBlock rule to add (AdBlockRule)
##        @param url URL that matched the rule (QUrl)
##        """
##        from .AdBlock.AdBlockPage import AdBlockedPageEntry
##        entry = AdBlockedPageEntry(rule, url)
##        if entry not in self.__adBlockedEntries:
##            self.__adBlockedEntries.append(entry)
##    
##    def getAdBlockedPageEntries(self):
##        """
##        Public method to get the list of AdBlock page entries.
##        
##        @return list of AdBlock page entries (list of AdBlockedPageEntry)
##        """
##        return self.__adBlockedEntries
    
    # TODO: User Agent Manager
##    def userAgent(self, resolveEmpty=False):
##        """
##        Public method to get the global user agent setting.
##        
##        @param resolveEmpty flag indicating to resolve an empty
##            user agent (boolean)
##        @return user agent string (string)
##        """
##        agent = Preferences.getWebBrowser("UserAgent")
##        if agent == "" and resolveEmpty:
##            agent = self.userAgentForUrl(QUrl())
##        return agent
##    
##    def setUserAgent(self, agent):
##        """
##        Public method to set the global user agent string.
##        
##        @param agent new current user agent string (string)
##        """
##        Preferences.setHelp("UserAgent", agent)
##    
##    def userAgentForUrl(self, url):
##        """
##        Public method to determine the user agent for the given URL.
##        
##        @param url URL to determine user agent for (QUrl)
##        @return user agent string (string)
##        """
##        import WebBrowser.WebBrowserWindow
##        agent = WebBrowser.WebBrowserWindow.WebBrowserWindow.userAgentsManager()\
##            .userAgentForUrl(url)
##        if agent == "":
##            # no agent string specified for the given host -> use global one
##            agent = Preferences.getWebBrowser("UserAgent")
##            if agent == "":
##                # no global agent string specified -> use default one
##                agent = QWebPage.userAgentForUrl(self, url)
##        return agent
##    
    # TODO: SSL
##    def __managerFinished(self, reply):
##        """
##        Private slot to handle a finished reply.
##        
##        This slot is used to get SSL related information for a reply.
##        
##        @param reply reference to the finished reply (QNetworkReply)
##        """
##        try:
##            frame = reply.request().originatingObject()
##        except AttributeError:
##            frame = None
##        
##        mainFrameRequest = frame == self.mainFrame()
##        
##        if mainFrameRequest and \
##           self.__sslConfiguration is not None and \
##           reply.url() == self.mainFrame().url():
##            self.__sslConfiguration = None
##        
##        if reply.error() == QNetworkReply.NoError and \
##           mainFrameRequest and \
##           self.__sslConfiguration is None and \
##           reply.url().scheme().lower() == "https" and \
##           reply.url() == self.mainFrame().url():
##            self.__sslConfiguration = reply.sslConfiguration()
##            self.__sslConfiguration.url = QUrl(reply.url())
##        
##        if reply.error() == QNetworkReply.NoError and \
##           mainFrameRequest and \
##           reply.url() == self.mainFrame().url():
##            modified = reply.header(QNetworkRequest.LastModifiedHeader)
##            if modified and modified.isValid():
##                import WebBrowser.WebBrowserWindow
##                manager = WebBrowser.WebBrowserWindow.WebBrowserWindow.bookmarksManager()
##                from .Bookmarks.BookmarkNode import BookmarkNode
##                for bookmark in manager.bookmarksForUrl(reply.url()):
##                    manager.setTimestamp(bookmark, BookmarkNode.TsModified,
##                                         modified)
    
##    def getSslCertificate(self):
##        """
##        Public method to get a reference to the SSL certificate.
##        
##        @return amended SSL certificate (QSslCertificate)
##        """
##        if self.__sslConfiguration is None:
##            return None
##        
##        sslInfo = self.__sslConfiguration.peerCertificate()
##        sslInfo.url = QUrl(self.__sslConfiguration.url)
##        return sslInfo
##    
##    def getSslCertificateChain(self):
##        """
##        Public method to get a reference to the SSL certificate chain.
##        
##        @return SSL certificate chain (list of QSslCertificate)
##        """
##        if self.__sslConfiguration is None:
##            return []
##        
##        chain = self.__sslConfiguration.peerCertificateChain()
##        return chain
##    
##    def getSslConfiguration(self):
##        """
##        Public method to return a reference to the current SSL configuration.
##        
##        @return reference to the SSL configuration in use (QSslConfiguration)
##        """
##        return self.__sslConfiguration
##    
##    def showSslInfo(self, pos):
##        """
##        Public slot to show some SSL information for the loaded page.
##        
##        @param pos position to show the info at (QPoint)
##        """
##        if SSL_AVAILABLE and self.__sslConfiguration is not None:
##            from E5Network.E5SslInfoWidget import E5SslInfoWidget
##            widget = E5SslInfoWidget(
##                self.mainFrame().url(), self.__sslConfiguration, self.view())
##            widget.showAt(pos)
##        else:
##            E5MessageBox.warning(
##                self.view(),
##                self.tr("SSL Info"),
##                self.tr("""This site does not contain SSL information."""))
##    
    def hasValidSslInfo(self):
        """
        Public method to check, if the page has a valid SSL certificate.
        
        @return flag indicating a valid SSL certificate (boolean)
        """
        if self.__sslConfiguration is None:
            return False
        
        certList = self.__sslConfiguration.peerCertificateChain()
        if not certList:
            return False
        
        certificateDict = Globals.toDict(
            Preferences.Prefs.settings.value("Ssl/CaCertificatesDict"))
        for server in certificateDict:
            localCAList = QSslCertificate.fromData(certificateDict[server])
            for cert in certList:
                if cert in localCAList:
                    return True
        
        for cert in certList:
            if cert.isBlacklisted():
                return False
        
        return True
    
##    @classmethod
##    def webPluginFactory(cls):
##        """
##        Class method to get a reference to the web plug-in factory
##        instance.
##        
##        @return reference to the web plug-in factory instance (WebPluginFactory
##        """
##        if cls._webPluginFactory is None:
##            from .WebPlugins.WebPluginFactory import WebPluginFactory
##            cls._webPluginFactory = WebPluginFactory()
##        
##        return cls._webPluginFactory
##    
##    def event(self, evt):
##        """
##        Public method implementing the event handler.
##        
##        @param evt reference to the event (QEvent)
##        @return flag indicating that the event was handled (boolean)
##        """
##        if evt.type() == QEvent.Leave:
##            # Fake a mouse move event just outside of the widget to trigger
##            # the WebKit event handler's mouseMoved function. This implements
##            # the interesting mouse-out behavior like invalidating scrollbars.
##            fakeEvent = QMouseEvent(QEvent.MouseMove, QPoint(0, -1),
##                                    Qt.NoButton, Qt.NoButton, Qt.NoModifier)
##            return super(HelpWebPage, self).event(fakeEvent)
##        
##        return super(HelpWebPage, self).event(evt)
##    
##    def __saveFrameStateRequested(self, frame, itm):
##        """
##        Private slot to save the page state (i.e. zoom level and scroll
##        position).
##        
##        Note: Code is based on qutebrowser.
##        
##        @param frame frame to be saved
##        @type QWebFrame
##        @param itm web history item to be saved
##        @type QWebHistoryItem
##        """
##        try:
##            if frame != self.mainFrame():
##                return
##        except RuntimeError:
##            # With Qt 5.2.1 (Ubuntu Trusty) we get this when closing a tab:
##            #     RuntimeError: wrapped C/C++ object of type BrowserPage has
##            #     been deleted
##            # Since the information here isn't that important for closing web
##            # views anyways, we ignore this error.
##            return
##        data = {
##            'zoom': frame.zoomFactor(),
##            'scrollPos': frame.scrollPosition(),
##        }
##        itm.setUserData(data)
##    
##    def __restoreFrameStateRequested(self, frame):
##        """
##        Private slot to restore scroll position and zoom level from
##        history.
##        
##        Note: Code is based on qutebrowser.
##        
##        @param frame frame to be restored
##        @type QWebFrame
##        """
##        if frame != self.mainFrame():
##            return
##        
##        data = self.history().currentItem().userData()
##        if data is None:
##            return
##        
##        if 'zoom' in data:
##            frame.page().view().setZoomValue(int(data['zoom'] * 100),
##                                             saveValue=False)
##        
##        if 'scrollPos' in data and frame.scrollPosition() == QPoint(0, 0):
##            frame.setScrollPosition(data['scrollPos'])
    
    def __featurePermissionRequested(self, url, feature):
        """
        Private slot handling a feature permission request.
        
        @param url url requesting the feature
        @type QUrl
        @param feature requested feature
        @type QWebEnginePage.Feature
        """
        manager = WebBrowser.WebBrowserWindow.WebBrowserWindow\
            .featurePermissionManager()
        manager.requestFeaturePermission(self, url, feature)
    
    def execJavaScript(self, script):
        """
        Public method to execute a JavaScript function synchroneously.
        
        @param script JavaScript script source to be executed
        @type str
        @return result of the script
        @rtype depending upon script result
        """
        loop = QEventLoop()
        resultDict = {"res": None}
        QTimer.singleShot(500, loop.quit);
        
        def resultCallback(res, resDict=resultDict):
            if loop and loop.isRunning():
                resDict["res"] = res
                loop.quit()
        
        self.runJavaScript(script, resultCallback)
        
        loop.exec_()
        return resultDict["res"]
    
    def scroll(self, x, y):
        """
        Public method to scroll by the given amount of pixels.
        
        @param x horizontal scroll value
        @type int
        @param y vertical scroll value
        @type int
        """
        self.runJavaScript(
            "window.scrollTo(window.scrollX + {0}, window.scrollY + {1})"
            .format(x, y)
        )
    
    def hitTestContent(self, pos):
        """
        Public method to test the content at a specified position.
        
        @param pos position to execute the test at
        @type QPoint
        @return test result object
        @rtype WebHitTestResult
        """
        return WebHitTestResult(self, pos)
    
    def __setupWebChannel(self):
        """
        Private method to setup a web channel to our external object.
        """
        oldChannel = self.webChannel()
        newChannel = QWebChannel(self)
        newChannel.registerObject("eric_object", ExternalJsObject(self))
        self.setWebChannel(newChannel)
        
        if oldChannel:
            del oldChannel.registeredObjects["eric_object"]
            del oldChannel
    
    def certificateError(self, error):
        """
        Public method to handle SSL certificate errors.
        
        @param error object containing the certificate error information
        @type QWebEngineCertificateError
        @return flag indicating to ignore this error
        @rtype bool
        """
        return WebBrowser.WebBrowserWindow.WebBrowserWindow.networkManager()\
            .certificateError(error, self.view())
    
    ##############################################
    ## Methods below deal with JavaScript messages
    ##############################################
    
    # TODO: JavaScript messages: do this right and add the others
    def javaScriptConsoleMessage(self, level, message, lineNumber,  sourceId):
        print("JS-console:", message, lineNumber, sourceId)
