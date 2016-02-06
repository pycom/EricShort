# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing the web browser using QWebEngineView.
"""

from __future__ import unicode_literals
try:
    str = unicode           # __IGNORE_EXCEPTION__
except NameError:
    pass

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QT_TRANSLATE_NOOP, \
    QUrl, QBuffer, QIODevice, QFileInfo, Qt, QTimer, QEvent, \
    QRect, QFile, QPoint, QByteArray, qVersion
from PyQt5.QtGui import QDesktopServices, QClipboard, QMouseEvent, QColor, \
    QPalette
from PyQt5.QtWidgets import qApp, QStyle, QMenu, QApplication, QInputDialog, \
    QLineEdit, QLabel, QToolTip, QFrame, QDialog
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from E5Gui import E5MessageBox, E5FileDialog

import WebBrowser
from .WebBrowserPage import WebBrowserPage

import Preferences
import UI.PixmapCache
import Globals

try:
    from PyQt5.QtNetwork import QSslCertificate
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False


class WebBrowserView(QWebEngineView):
    """
    Class implementing the web browser view widget.
    
    @signal sourceChanged(QUrl) emitted after the current URL has changed
    @signal forwardAvailable(bool) emitted after the current URL has changed
    @signal backwardAvailable(bool) emitted after the current URL has changed
    @signal highlighted(str) emitted, when the mouse hovers over a link
    @signal search(QUrl) emitted, when a search is requested
    @signal zoomValueChanged(int) emitted to signal a change of the zoom value
    """
    sourceChanged = pyqtSignal(QUrl)
    forwardAvailable = pyqtSignal(bool)
    backwardAvailable = pyqtSignal(bool)
    highlighted = pyqtSignal(str)
    search = pyqtSignal(QUrl)
    zoomValueChanged = pyqtSignal(int)
    
    ZoomLevels = [
        30, 40, 50, 67, 80, 90,
        100,
        110, 120, 133, 150, 170, 200, 220, 233, 250, 270, 285, 300,
    ]
    ZoomLevelDefault = 100
    
    def __init__(self, mainWindow, parent=None, name=""):
        """
        Constructor
        
        @param mainWindow reference to the main window (WebBrowserWindow)
        @param parent parent widget of this window (QWidget)
        @param name name of this window (string)
        """
        super(WebBrowserView, self).__init__(parent)
        self.setObjectName(name)
        
        self.__rwhvqt = None
        self.installEventFilter(self)
##        
##        import Helpviewer.HelpWindow
##        self.__speedDial = Helpviewer.HelpWindow.HelpWindow.speedDial()
        
        self.__page = WebBrowserPage(self)
        self.setPage(self.__page)
        
        self.__mw = mainWindow
        self.__ctrlPressed = False
        self.__isLoading = False
        self.__progress = 0
        
        self.__currentZoom = 100
        self.__zoomLevels = WebBrowserView.ZoomLevels[:]
##        
##        self.__javaScriptBinding = None
##        self.__javaScriptEricObject = None
        
##        self.__mw.zoomTextOnlyChanged.connect(self.__applyZoom)
        
##        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
##        self.linkClicked.connect(self.setSource)
##        
        self.urlChanged.connect(self.__urlChanged)
##        self.statusBarMessage.connect(self.__statusBarMessage)
        self.page().linkHovered.connect(self.__linkHovered)
        
        self.loadStarted.connect(self.__loadStarted)
        self.loadProgress.connect(self.__loadProgress)
        self.loadFinished.connect(self.__loadFinished)
        
##        self.page().setForwardUnsupportedContent(True)
##        self.page().unsupportedContent.connect(self.__unsupportedContent)
        
##        self.page().frameCreated.connect(self.__addExternalBinding)
##        self.__addExternalBinding(self.page().mainFrame())
        
##        self.page().databaseQuotaExceeded.connect(self.__databaseQuotaExceeded)
        
        # TODO: Open Search
##        self.__mw.openSearchManager().currentEngineChanged.connect(
##            self.__currentEngineChanged)
        
        self.setAcceptDrops(True)
        
        # TODO: Access Keys
##        self.__enableAccessKeys = Preferences.getHelp("AccessKeysEnabled")
##        self.__accessKeysPressed = False
##        self.__accessKeyLabels = []
##        self.__accessKeyNodes = {}
##        
##        self.page().loadStarted.connect(self.__hideAccessKeys)
##        self.page().scrollRequested.connect(self.__hideAccessKeys)
        
        self.__rss = []
        
        self.__clickedFrame = None
        
        # TODO: PIM
##        self.__mw.personalInformationManager().connectPage(self.page())
        # TODO: GreaseMonkey
##        self.__mw.greaseMonkeyManager().connectPage(self.page())
        
        # TODO: WebInspector
##        self.__inspector = None
        
        self.grabGesture(Qt.PinchGesture)
    
##    def __addExternalBinding(self, frame=None):
##        """
##        Private slot to add javascript bindings for adding search providers.
##        
##        @param frame reference to the web frame (QWebFrame)
##        """
##        self.page().settings().setAttribute(QWebSettings.JavascriptEnabled,
##                                            True)
##        if self.__javaScriptBinding is None:
##            self.__javaScriptBinding = JavaScriptExternalObject(self.__mw, self)
##        
##        if frame is None:
##            # called from QWebFrame.javaScriptWindowObjectCleared
##            frame = self.sender()
##            if isinstance(frame, HelpWebPage):
##                frame = frame.mainFrame()
##            if frame.url().scheme() == "eric" and frame.url().path() == "home":
##                if self.__javaScriptEricObject is None:
##                    self.__javaScriptEricObject = JavaScriptEricObject(
##                        self.__mw, self)
##                frame.addToJavaScriptWindowObject(
##                    "eric", self.__javaScriptEricObject)
##            elif frame.url().scheme() == "eric" and \
##                    frame.url().path() == "speeddial":
##                frame.addToJavaScriptWindowObject(
##                    "speeddial", self.__speedDial)
##                self.__speedDial.addWebFrame(frame)
##        else:
##            # called from QWebPage.frameCreated
##            frame.javaScriptWindowObjectCleared.connect(
##                self.__addExternalBinding)
##        frame.addToJavaScriptWindowObject("external", self.__javaScriptBinding)
##    
##    def linkedResources(self, relation=""):
##        """
##        Public method to extract linked resources.
##        
##        @param relation relation to extract (string)
##        @return list of linked resources (list of LinkedResource)
##        """
##        resources = []
##        
##        baseUrl = self.page().mainFrame().baseUrl()
##        
##        linkElements = self.page().mainFrame().findAllElements(
##            "html > head > link")
##        
##        for linkElement in linkElements.toList():
##            rel = linkElement.attribute("rel")
##            href = linkElement.attribute("href")
##            type_ = linkElement.attribute("type")
##            title = linkElement.attribute("title")
##            
##            if href == "" or type_ == "":
##                continue
##            if relation and rel != relation:
##                continue
##            
##            resource = LinkedResource()
##            resource.rel = rel
##            resource.type_ = type_
##            resource.href = baseUrl.resolved(
##                QUrl.fromEncoded(href.encode("utf-8")))
##            resource.title = title
##            
##            resources.append(resource)
##        
##        return resources
##    
##    def __currentEngineChanged(self):
##        """
##        Private slot to track a change of the current search engine.
##        """
##        if self.url().toString() == "eric:home":
##            self.reload()
    
    # TODO: eliminate requestData, add param to get rid of __ctrlPressed
    def setSource(self, name, requestData=None):
        """
        Public method used to set the source to be displayed.
        
        @param name filename to be shown (QUrl)
        @param requestData tuple containing the request data (QNetworkRequest,
            QNetworkAccessManager.Operation, QByteArray)
        """
##        if (name is None or not name.isValid()) and requestData is None:
        if name is None or not name.isValid():
            return
        
##        if name is None and requestData is not None:
##            name = requestData[0].url()
##        
        if self.__ctrlPressed:
            # open in a new window
            self.__mw.newTab(name)
            self.__ctrlPressed = False
            return
        
        if not name.scheme():
            name.setUrl(Preferences.getWebBrowser("DefaultScheme") +
                        name.toString())
        
        # TODO: move some of this to web page
        if len(name.scheme()) == 1 or \
           name.scheme() == "file":
            # name is a local file
            if name.scheme() and len(name.scheme()) == 1:
                # it is a local path on win os
                name = QUrl.fromLocalFile(name.toString())
            
            if not QFileInfo(name.toLocalFile()).exists():
                E5MessageBox.critical(
                    self,
                    self.tr("eric6 Web Browser"),
                    self.tr(
                        """<p>The file <b>{0}</b> does not exist.</p>""")
                    .format(name.toLocalFile()))
                return

            if name.toLocalFile().endswith(".pdf") or \
               name.toLocalFile().endswith(".PDF") or \
               name.toLocalFile().endswith(".chm") or \
               name.toLocalFile().endswith(".CHM"):
                started = QDesktopServices.openUrl(name)
                if not started:
                    E5MessageBox.critical(
                        self,
                        self.tr("eric6 Web Browser"),
                        self.tr(
                            """<p>Could not start a viewer"""
                            """ for file <b>{0}</b>.</p>""")
                        .format(name.path()))
                return
        elif name.scheme() in ["mailto"]:
            started = QDesktopServices.openUrl(name)
            if not started:
                E5MessageBox.critical(
                    self,
                    self.tr("eric6 Web Browser"),
                    self.tr(
                        """<p>Could not start an application"""
                        """ for URL <b>{0}</b>.</p>""")
                    .format(name.toString()))
            return
##        elif name.scheme() == "javascript":
##            scriptSource = QUrl.fromPercentEncoding(name.toString(
##                QUrl.FormattingOptions(QUrl.TolerantMode | QUrl.RemoveScheme)))
##            self.page().mainFrame().evaluateJavaScript(scriptSource)
##            return
        else:
            if name.toString().endswith(".pdf") or \
               name.toString().endswith(".PDF") or \
               name.toString().endswith(".chm") or \
               name.toString().endswith(".CHM"):
                started = QDesktopServices.openUrl(name)
                if not started:
                    E5MessageBox.critical(
                        self,
                        self.tr("eric6 Web Browser"),
                        self.tr(
                            """<p>Could not start a viewer"""
                            """ for file <b>{0}</b>.</p>""")
                        .format(name.path()))
                return
        
        if requestData is not None:
            self.load(*requestData)
        else:
            self.load(name)

    def source(self):
        """
        Public method to return the URL of the loaded page.
        
        @return URL loaded in the help browser (QUrl)
        """
        return self.url()
    
    def documentTitle(self):
        """
        Public method to return the title of the loaded page.
        
        @return title (string)
        """
        return self.title()
    
    def backward(self):
        """
        Public slot to move backwards in history.
        """
        self.triggerPageAction(QWebEnginePage.Back)
        self.__urlChanged(self.history().currentItem().url())
    
    def forward(self):
        """
        Public slot to move forward in history.
        """
        self.triggerPageAction(QWebEnginePage.Forward)
        self.__urlChanged(self.history().currentItem().url())
    
    def home(self):
        """
        Public slot to move to the first page loaded.
        """
##        homeUrl = QUrl("http://localhost")
##        # TODO: eric: scheme or Configuration page
        homeUrl = QUrl(Preferences.getWebBrowser("HomePage"))
        self.setSource(homeUrl)
        self.__urlChanged(self.history().currentItem().url())
    
    def reload(self):
        """
        Public slot to reload the current page.
        """
        self.triggerPageAction(QWebEnginePage.Reload)
    
    def copy(self):
        """
        Public slot to copy the selected text.
        """
        self.triggerPageAction(QWebEnginePage.Copy)
    
    def isForwardAvailable(self):
        """
        Public method to determine, if a forward move in history is possible.
        
        @return flag indicating move forward is possible (boolean)
        """
        return self.history().canGoForward()
    
    def isBackwardAvailable(self):
        """
        Public method to determine, if a backwards move in history is possible.
        
        @return flag indicating move backwards is possible (boolean)
        """
        return self.history().canGoBack()
    
    def __levelForZoom(self, zoom):
        """
        Private method determining the zoom level index given a zoom factor.
        
        @param zoom zoom factor (integer)
        @return index of zoom factor (integer)
        """
        try:
            index = self.__zoomLevels.index(zoom)
        except ValueError:
            for index in range(len(self.__zoomLevels)):
                if zoom <= self.__zoomLevels[index]:
                    break
        return index
    
    def __applyZoom(self):
        """
        Private slot to apply the current zoom factor.
        """
        self.setZoomValue(self.__currentZoom)
    
    def setZoomValue(self, value, saveValue=True):
        """
        Public method to set the zoom value.
        
        @param value zoom value (integer)
        @keyparam saveValue flag indicating to save the zoom value with the
            zoom manager
        @type bool
        """
        if value != self.zoomValue():
            self.setZoomFactor(value / 100.0)
            self.__currentZoom = value
            # TODO: Zoom Manager
##            if saveValue:
##                Helpviewer.HelpWindow.HelpWindow.zoomManager().setZoomValue(
##                    self.url(), value)
            self.zoomValueChanged.emit(value)
    
    def zoomValue(self):
        """
        Public method to get the current zoom value.
        
        @return zoom value (integer)
        """
        val = self.zoomFactor() * 100
        return int(val)
    
    def zoomIn(self):
        """
        Public slot to zoom into the page.
        """
        index = self.__levelForZoom(self.__currentZoom)
        if index < len(self.__zoomLevels) - 1:
            self.__currentZoom = self.__zoomLevels[index + 1]
        self.__applyZoom()
    
    def zoomOut(self):
        """
        Public slot to zoom out of the page.
        """
        index = self.__levelForZoom(self.__currentZoom)
        if index > 0:
            self.__currentZoom = self.__zoomLevels[index - 1]
        self.__applyZoom()
    
    def zoomReset(self):
        """
        Public method to reset the zoom factor.
        """
        index = self.__levelForZoom(WebBrowserView.ZoomLevelDefault)
        self.__currentZoom = self.__zoomLevels[index]
        self.__applyZoom()
    
    def hasSelection(self):
        """
        Public method to determine, if there is some text selected.
        
        @return flag indicating text has been selected (boolean)
        """
        return self.selectedText() != ""
    
    # TODO: adjust this to what Qt 5.6 is offering
    def findNextPrev(self, txt, case, backwards, wrap, highlightAll, callback):
        """
        Public slot to find the next occurrence of a text.
        
        @param txt text to search for (string)
        @param case flag indicating a case sensitive search (boolean)
        @param backwards flag indicating a backwards search (boolean)
        @param wrap flag indicating to wrap around (boolean)
        @param highlightAll flag indicating to highlight all occurrences
            (boolean)
        @param callback reference to a function with a bool parameter
        @type function(bool) or None
        """
        
        findFlags = QWebEnginePage.FindFlags()
        if case:
            findFlags |= QWebEnginePage.FindCaseSensitively
        if backwards:
            findFlags |= QWebEnginePage.FindBackward
##        if wrap:
##            findFlags |= QWebPage.FindWrapsAroundDocument
##        try:
##            if highlightAll:
##                findFlags |= QWebPage.HighlightAllOccurrences
##        except AttributeError:
##            pass
        
        if callback is None:
            self.findText(txt, findFlags)
        else:
            self.findText(txt, findFlags, callback)
    
    # TODO: WebBrowserWebElement
##    def __isMediaElement(self, element):
##        """
##        Private method to check, if the given element is a media element.
##        
##        @param element element to be checked (QWebElement)
##        @return flag indicating a media element (boolean)
##        """
##        return element.tagName().lower() in ["video", "audio"]
    
    def contextMenuEvent(self, evt):
        """
        Protected method called to create a context menu.
        
        This method is overridden from QWebEngineView.
        
        @param evt reference to the context menu event object
            (QContextMenuEvent)
        """
        # TODO: User Agent
##        from .UserAgent.UserAgentMenu import UserAgentMenu
        menu = QMenu(self)
        
##        frameAtPos = self.page().frameAt(evt.pos())
        # TODO: WebHitTestResult
##        hit = self.page().hitTestContent(evt.pos())
##        if not hit.linkUrl().isEmpty():
##            menu.addAction(
##                UI.PixmapCache.getIcon("openNewTab.png"),
##                self.tr("Open Link in New Tab\tCtrl+LMB"),
##                self.__openLinkInNewTab).setData(hit.linkUrl())
##            menu.addSeparator()
##            menu.addAction(
##                UI.PixmapCache.getIcon("download.png"),
##                self.tr("Save Lin&k"), self.__downloadLink)
##            menu.addAction(
##                UI.PixmapCache.getIcon("bookmark22.png"),
##                self.tr("Bookmark this Link"), self.__bookmarkLink)\
##                .setData(hit.linkUrl())
##            menu.addSeparator()
##            menu.addAction(
##                UI.PixmapCache.getIcon("editCopy.png"),
##                self.tr("Copy Link to Clipboard"), self.__copyLink)
##            menu.addAction(
##                UI.PixmapCache.getIcon("mailSend.png"),
##                self.tr("Send Link"),
##                self.__sendLink).setData(hit.linkUrl())
##            if Preferences.getHelp("VirusTotalEnabled") and \
##               Preferences.getHelp("VirusTotalServiceKey") != "":
##                menu.addAction(
##                    UI.PixmapCache.getIcon("virustotal.png"),
##                    self.tr("Scan Link with VirusTotal"),
##                    self.__virusTotal).setData(hit.linkUrl())
        
##        if not hit.imageUrl().isEmpty():
##            if not menu.isEmpty():
##                menu.addSeparator()
##            menu.addAction(
##                UI.PixmapCache.getIcon("openNewTab.png"),
##                self.tr("Open Image in New Tab"),
##                self.__openLinkInNewTab).setData(hit.imageUrl())
##            menu.addSeparator()
##            menu.addAction(
##                UI.PixmapCache.getIcon("download.png"),
##                self.tr("Save Image"), self.__downloadImage)
##            menu.addAction(
##                self.tr("Copy Image to Clipboard"), self.__copyImage)
##            menu.addAction(
##                UI.PixmapCache.getIcon("editCopy.png"),
##                self.tr("Copy Image Location to Clipboard"),
##                self.__copyLocation).setData(hit.imageUrl().toString())
##            menu.addAction(
##                UI.PixmapCache.getIcon("mailSend.png"),
##                self.tr("Send Image Link"),
##                self.__sendLink).setData(hit.imageUrl())
##            menu.addSeparator()
##            menu.addAction(
##                UI.PixmapCache.getIcon("adBlockPlus.png"),
##                self.tr("Block Image"), self.__blockImage)\
##                .setData(hit.imageUrl().toString())
##            if Preferences.getHelp("VirusTotalEnabled") and \
##               Preferences.getHelp("VirusTotalServiceKey") != "":
##                menu.addAction(
##                    UI.PixmapCache.getIcon("virustotal.png"),
##                    self.tr("Scan Image with VirusTotal"),
##                    self.__virusTotal).setData(hit.imageUrl())
        
##        element = hit.element()
##        if not element.isNull():
##            if self.__isMediaElement(element):
##                if not menu.isEmpty():
##                    menu.addSeparator()
##                
##                self.__clickedMediaElement = element
##                
##                paused = element.evaluateJavaScript("this.paused")
##                muted = element.evaluateJavaScript("this.muted")
##                videoUrl = QUrl(element.evaluateJavaScript("this.currentSrc"))
##                
##                if paused:
##                    menu.addAction(
##                        UI.PixmapCache.getIcon("mediaPlaybackStart.png"),
##                        self.tr("Play"), self.__pauseMedia)
##                else:
##                    menu.addAction(
##                        UI.PixmapCache.getIcon("mediaPlaybackPause.png"),
##                        self.tr("Pause"), self.__pauseMedia)
##                if muted:
##                    menu.addAction(
##                        UI.PixmapCache.getIcon("audioVolumeHigh.png"),
##                        self.tr("Unmute"), self.__muteMedia)
##                else:
##                    menu.addAction(
##                        UI.PixmapCache.getIcon("audioVolumeMuted.png"),
##                        self.tr("Mute"), self.__muteMedia)
##                menu.addSeparator()
##                menu.addAction(
##                    UI.PixmapCache.getIcon("editCopy.png"),
##                    self.tr("Copy Media Address to Clipboard"),
##                    self.__copyLocation).setData(videoUrl.toString())
##                menu.addAction(
##                    UI.PixmapCache.getIcon("mailSend.png"),
##                    self.tr("Send Media Address"), self.__sendLink)\
##                    .setData(videoUrl)
##                menu.addAction(
##                    UI.PixmapCache.getIcon("download.png"),
##                    self.tr("Save Media"), self.__downloadMedia)\
##                    .setData(videoUrl)
##            
##            if element.tagName().lower() in ["input", "textarea"]:
##                if menu.isEmpty():
##                    pageMenu = self.page().createStandardContextMenu()
##                    directionFound = False
##                    # used to detect double direction entry
##                    for act in pageMenu.actions():
##                        if act.isSeparator():
##                            menu.addSeparator()
##                            continue
##                        if act.menu():
##                            if self.pageAction(
##                                    QWebPage.SetTextDirectionDefault) in \
##                                    act.menu().actions():
##                                if directionFound:
##                                    act.setVisible(False)
##                                directionFound = True
##                            elif self.pageAction(QWebPage.ToggleBold) in \
##                                    act.menu().actions():
##                                act.setVisible(False)
##                        elif act == self.pageAction(QWebPage.InspectElement):
##                            # we have our own inspect entry
##                            act.setVisible(False)
##                        menu.addAction(act)
##                    pageMenu = None
        
        if not menu.isEmpty():
            menu.addSeparator()
        
        # TODO: PIM
##        self.__mw.personalInformationManager().createSubMenu(menu, self, hit)
        
        menu.addAction(self.__mw.newTabAct)
        menu.addAction(self.__mw.newAct)
        menu.addSeparator()
##        menu.addAction(self.__mw.saveAsAct)
##        menu.addSeparator()
        
##        if frameAtPos and self.page().mainFrame() != frameAtPos:
##            self.__clickedFrame = frameAtPos
##            fmenu = QMenu(self.tr("This Frame"))
##            frameUrl = self.__clickedFrame.url()
##            if frameUrl.isValid():
##                fmenu.addAction(
##                    self.tr("Show &only this frame"),
##                    self.__loadClickedFrame)
##                fmenu.addAction(
##                    UI.PixmapCache.getIcon("openNewTab.png"),
##                    self.tr("Show in new &tab"),
##                    self.__openLinkInNewTab).setData(self.__clickedFrame.url())
##                fmenu.addSeparator()
##            fmenu.addAction(
##                UI.PixmapCache.getIcon("print.png"),
##                self.tr("&Print"), self.__printClickedFrame)
##            fmenu.addAction(
##                UI.PixmapCache.getIcon("printPreview.png"),
##                self.tr("Print Preview"), self.__printPreviewClickedFrame)
##            fmenu.addAction(
##                UI.PixmapCache.getIcon("printPdf.png"),
##                self.tr("Print as PDF"), self.__printPdfClickedFrame)
##            fmenu.addSeparator()
##            fmenu.addAction(
##                UI.PixmapCache.getIcon("zoomIn.png"),
##                self.tr("Zoom &in"), self.__zoomInClickedFrame)
##            fmenu.addAction(
##                UI.PixmapCache.getIcon("zoomReset.png"),
##                self.tr("Zoom &reset"), self.__zoomResetClickedFrame)
##            fmenu.addAction(
##                UI.PixmapCache.getIcon("zoomOut.png"),
##                self.tr("Zoom &out"), self.__zoomOutClickedFrame)
##            fmenu.addSeparator()
##            fmenu.addAction(
##                self.tr("Show frame so&urce"),
##                self.__showClickedFrameSource)
##            
##            menu.addMenu(fmenu)
##            menu.addSeparator()
        
        # TODO: Bookmarks
##        menu.addAction(
##            UI.PixmapCache.getIcon("bookmark22.png"),
##            self.tr("Bookmark this Page"), self.addBookmark)
        menu.addAction(
            UI.PixmapCache.getIcon("mailSend.png"),
            self.tr("Send Page Link"), self.__sendLink).setData(self.url())
        menu.addSeparator()
        # TODO: User Agent
##        self.__userAgentMenu = UserAgentMenu(self.tr("User Agent"),
##                                             url=self.url())
##        menu.addMenu(self.__userAgentMenu)
##        menu.addSeparator()
        menu.addAction(self.__mw.backAct)
        menu.addAction(self.__mw.forwardAct)
        menu.addAction(self.__mw.homeAct)
        menu.addSeparator()
        menu.addAction(self.__mw.zoomInAct)
        menu.addAction(self.__mw.zoomResetAct)
        menu.addAction(self.__mw.zoomOutAct)
        menu.addSeparator()
        if self.selectedText():
            menu.addAction(self.__mw.copyAct)
            menu.addAction(
                UI.PixmapCache.getIcon("mailSend.png"),
                self.tr("Send Text"),
                self.__sendLink).setData(self.selectedText())
        menu.addAction(self.__mw.findAct)
        menu.addSeparator()
        if self.selectedText():
            # TODO: Open Search
##            self.__searchMenu = menu.addMenu(self.tr("Search with..."))
##            
##            from .OpenSearch.OpenSearchEngineAction import \
##                OpenSearchEngineAction
##            engineNames = self.__mw.openSearchManager().allEnginesNames()
##            for engineName in engineNames:
##                engine = self.__mw.openSearchManager().engine(engineName)
##                act = OpenSearchEngineAction(engine, self.__searchMenu)
##                act.setData(engineName)
##                self.__searchMenu.addAction(act)
##            self.__searchMenu.triggered.connect(self.__searchRequested)
##            
##            menu.addSeparator()
            
            # TODO: Languages Dialog
##            from .HelpLanguagesDialog import HelpLanguagesDialog
##            languages = Preferences.toList(
##                Preferences.Prefs.settings.value(
##                    "Help/AcceptLanguages",
##                    HelpLanguagesDialog.defaultAcceptLanguages()))
##            if languages:
##                language = languages[0]
##                langCode = language.split("[")[1][:2]
##                googleTranslatorUrl = QUrl(
##                    "http://translate.google.com/#auto|{0}|{1}".format(
##                        langCode, self.selectedText()))
##                menu.addAction(
##                    UI.PixmapCache.getIcon("translate.png"),
##                    self.tr("Google Translate"), self.__openLinkInNewTab)\
##                    .setData(googleTranslatorUrl)
##                wiktionaryUrl = QUrl(
##                    "http://{0}.wiktionary.org/wiki/Special:Search?search={1}"
##                    .format(langCode, self.selectedText()))
##                menu.addAction(
##                    UI.PixmapCache.getIcon("wikipedia.png"),
##                    self.tr("Dictionary"), self.__openLinkInNewTab)\
##                    .setData(wiktionaryUrl)
##                menu.addSeparator()
            
            guessedUrl = QUrl.fromUserInput(self.selectedText().strip())
            if self.__isUrlValid(guessedUrl):
                menu.addAction(
                    self.tr("Go to web address"),
                    self.__openLinkInNewTab).setData(guessedUrl)
                menu.addSeparator()
##        
##        element = hit.element()
##        if not element.isNull() and \
##           element.tagName().lower() == "input" and \
##           element.attribute("type", "text") == "text":
##            menu.addAction(self.tr("Add to web search toolbar"),
##                           self.__addSearchEngine).setData(element)
##            menu.addSeparator()
        
        # TODO: Web Inspector
##        menu.addAction(
##            UI.PixmapCache.getIcon("webInspector.png"),
##            self.tr("Web Inspector..."), self.__webInspector)
        
        menu.exec_(evt.globalPos())
    
    def __isUrlValid(self, url):
        """
        Private method to check a URL for validity.
        
        @param url URL to be checked (QUrl)
        @return flag indicating a valid URL (boolean)
        """
        return url.isValid() and \
            bool(url.host()) and \
            bool(url.scheme()) and \
            "." in url.host()
    
    def __openLinkInNewTab(self):
        """
        Private method called by the context menu to open a link in a new
        window.
        """
        act = self.sender()
        url = act.data()
        if url.isEmpty():
            return
        
        # TODO: check, if this can be done simpler
        self.__ctrlPressed = True
        self.setSource(url)
        self.__ctrlPressed = False
    
    # TODO: Bookmarks
##    def __bookmarkLink(self):
##        """
##        Private slot to bookmark a link via the context menu.
##        """
##        act = self.sender()
##        url = act.data()
##        if url.isEmpty():
##            return
##        
##        from .Bookmarks.AddBookmarkDialog import AddBookmarkDialog
##        dlg = AddBookmarkDialog()
##        dlg.setUrl(bytes(url.toEncoded()).decode())
##        dlg.exec_()
    
    def __sendLink(self):
        """
        Private slot to send a link via email.
        """
        act = self.sender()
        data = act.data()
        if isinstance(data, QUrl) and data.isEmpty():
            return
        
        if isinstance(data, QUrl):
            data = data.toString()
        QDesktopServices.openUrl(QUrl("mailto:?body=" + data))
    
##    def __downloadLink(self):
##        """
##        Private slot to download a link and save it to disk.
##        """
##        self.pageAction(QWebPage.DownloadLinkToDisk).trigger()
##    
##    def __copyLink(self):
##        """
##        Private slot to copy a link to the clipboard.
##        """
##        self.pageAction(QWebPage.CopyLinkToClipboard).trigger()
##    
##    def __downloadImage(self):
##        """
##        Private slot to download an image and save it to disk.
##        """
##        self.pageAction(QWebPage.DownloadImageToDisk).trigger()
##    
##    def __copyImage(self):
##        """
##        Private slot to copy an image to the clipboard.
##        """
##        self.pageAction(QWebPage.CopyImageToClipboard).trigger()
    
    def __copyLocation(self):
        """
        Private slot to copy an image or media location to the clipboard.
        """
        act = self.sender()
        url = act.data()
        QApplication.clipboard().setText(url)
    
    # TODO: AdBlock
##    def __blockImage(self):
##        """
##        Private slot to add a block rule for an image URL.
##        """
##        import Helpviewer.HelpWindow
##        act = self.sender()
##        url = act.data()
##        dlg = Helpviewer.HelpWindow.HelpWindow.adBlockManager().showDialog()
##        dlg.addCustomRule(url)
    
    # TODO: DownloadManager
    def __downloadMedia(self):
        """
        Private slot to download a media and save it to disk.
        """
        act = self.sender()
        url = act.data()
        self.__mw.downloadManager().download(url, True, mainWindow=self.__mw)
    
    # TODO: this needs to be changed
##    def __pauseMedia(self):
##        """
##        Private slot to pause or play the selected media.
##        """
##        paused = self.__clickedMediaElement.evaluateJavaScript("this.paused")
##        
##        if paused:
##            self.__clickedMediaElement.evaluateJavaScript("this.play()")
##        else:
##            self.__clickedMediaElement.evaluateJavaScript("this.pause()")
##    
##    def __muteMedia(self):
##        """
##        Private slot to (un)mute the selected media.
##        """
##        muted = self.__clickedMediaElement.evaluateJavaScript("this.muted")
##        
##        if muted:
##            self.__clickedMediaElement.evaluateJavaScript("this.muted = false")
##        else:
##            self.__clickedMediaElement.evaluateJavaScript("this.muted = true")
    
    # TODO: VirusTotal
##    def __virusTotal(self):
##        """
##        Private slot to scan the selected URL with VirusTotal.
##        """
##        act = self.sender()
##        url = act.data()
##        self.__mw.requestVirusTotalScan(url)
    
    # TODO OpenSearch
##    def __searchRequested(self, act):
##        """
##        Private slot to search for some text with a selected search engine.
##        
##        @param act reference to the action that triggered this slot (QAction)
##        """
##        searchText = self.selectedText()
##        
##        if not searchText:
##            return
##        
##        engineName = act.data()
##        if engineName:
##            engine = self.__mw.openSearchManager().engine(engineName)
##            self.search.emit(engine.searchUrl(searchText))
##    
##    def __addSearchEngine(self):
##        """
##        Private slot to add a new search engine.
##        """
##        act = self.sender()
##        if act is None:
##            return
##        
##        element = act.data()
##        elementName = element.attribute("name")
##        formElement = QWebElement(element)
##        while formElement.tagName().lower() != "form":
##            formElement = formElement.parent()
##        
##        if formElement.isNull() or \
##           formElement.attribute("action") == "":
##            return
##        
##        method = formElement.attribute("method", "get").lower()
##        if method != "get":
##            E5MessageBox.warning(
##                self,
##                self.tr("Method not supported"),
##                self.tr(
##                    """{0} method is not supported.""").format(method.upper()))
##            return
##        
##        searchUrl = QUrl(self.page().mainFrame().baseUrl().resolved(
##            QUrl(formElement.attribute("action"))))
##        if searchUrl.scheme() != "http":
##            return
##        
##        if qVersion() >= "5.0.0":
##            from PyQt5.QtCore import QUrlQuery
##            searchUrlQuery = QUrlQuery(searchUrl)
##        searchEngines = {}
##        inputFields = formElement.findAll("input")
##        for inputField in inputFields.toList():
##            type_ = inputField.attribute("type", "text")
##            name = inputField.attribute("name")
##            value = inputField.evaluateJavaScript("this.value")
##            
##            if type_ == "submit":
##                searchEngines[value] = name
##            elif type_ == "text":
##                if inputField == element:
##                    value = "{searchTerms}"
##                if qVersion() >= "5.0.0":
##                    searchUrlQuery.addQueryItem(name, value)
##                else:
##                    searchUrl.addQueryItem(name, value)
##            elif type_ == "checkbox" or type_ == "radio":
##                if inputField.evaluateJavaScript("this.checked"):
##                    if qVersion() >= "5.0.0":
##                        searchUrlQuery.addQueryItem(name, value)
##                    else:
##                        searchUrl.addQueryItem(name, value)
##            elif type_ == "hidden":
##                if qVersion() >= "5.0.0":
##                    searchUrlQuery.addQueryItem(name, value)
##                else:
##                    searchUrl.addQueryItem(name, value)
##        
##        selectFields = formElement.findAll("select")
##        for selectField in selectFields.toList():
##            name = selectField.attribute("name")
##            selectedIndex = selectField.evaluateJavaScript(
##                "this.selectedIndex")
##            if selectedIndex == -1:
##                continue
##            
##            options = selectField.findAll("option")
##            value = options.at(selectedIndex).toPlainText()
##            if qVersion() >= "5.0.0":
##                searchUrlQuery.addQueryItem(name, value)
##            else:
##                searchUrl.addQueryItem(name, value)
##        
##        ok = True
##        if len(searchEngines) > 1:
##            searchEngine, ok = QInputDialog.getItem(
##                self,
##                self.tr("Search engine"),
##                self.tr("Choose the desired search engine"),
##                sorted(searchEngines.keys()), 0, False)
##            
##            if not ok:
##                return
##            
##            if searchEngines[searchEngine] != "":
##                if qVersion() >= "5.0.0":
##                    searchUrlQuery.addQueryItem(
##                        searchEngines[searchEngine], searchEngine)
##                else:
##                    searchUrl.addQueryItem(
##                        searchEngines[searchEngine], searchEngine)
##        engineName = ""
##        labels = formElement.findAll('label[for="{0}"]'.format(elementName))
##        if labels.count() > 0:
##            engineName = labels.at(0).toPlainText()
##        
##        engineName, ok = QInputDialog.getText(
##            self,
##            self.tr("Engine name"),
##            self.tr("Enter a name for the engine"),
##            QLineEdit.Normal,
##            engineName)
##        if not ok:
##            return
##        
##        if qVersion() >= "5.0.0":
##            searchUrl.setQuery(searchUrlQuery)
##        
##        from .OpenSearch.OpenSearchEngine import OpenSearchEngine
##        engine = OpenSearchEngine()
##        engine.setName(engineName)
##        engine.setDescription(engineName)
##        engine.setSearchUrlTemplate(searchUrl.toString())
##        engine.setImage(self.icon().pixmap(16, 16).toImage())
##        
##        self.__mw.openSearchManager().addEngine(engine)
    
    # TODO: WebInspector
##    def __webInspector(self):
##        """
##        Private slot to show the web inspector window.
##        """
##        if self.__inspector is None:
##            from .HelpInspector import HelpInspector
##            self.__inspector = HelpInspector()
##            self.__inspector.setPage(self.page())
##            self.__inspector.show()
##        elif self.__inspector.isVisible():
##            self.__inspector.hide()
##        else:
##            self.__inspector.show()
##    
##    def closeWebInspector(self):
##        """
##        Public slot to close the web inspector.
##        """
##        if self.__inspector is not None:
##            if self.__inspector.isVisible():
##                self.__inspector.hide()
##            self.__inspector.deleteLater()
##            self.__inspector = None
    
    # TODO: Bookmarks
##    def addBookmark(self):
##        """
##        Public slot to bookmark the current page.
##        """
##        from .Bookmarks.AddBookmarkDialog import AddBookmarkDialog
##        dlg = AddBookmarkDialog()
##        dlg.setUrl(bytes(self.url().toEncoded()).decode())
##        dlg.setTitle(self.title())
##        meta = self.page().mainFrame().metaData()
##        if "description" in meta:
##            dlg.setDescription(meta["description"][0])
##        dlg.exec_()
    
    def dragEnterEvent(self, evt):
        """
        Protected method called by a drag enter event.
        
        @param evt reference to the drag enter event (QDragEnterEvent)
        """
        evt.acceptProposedAction()
    
    def dragMoveEvent(self, evt):
        """
        Protected method called by a drag move event.
        
        @param evt reference to the drag move event (QDragMoveEvent)
        """
        evt.ignore()
        if evt.source() != self:
            if len(evt.mimeData().urls()) > 0:
                evt.acceptProposedAction()
            else:
                url = QUrl(evt.mimeData().text())
                if url.isValid():
                    evt.acceptProposedAction()
        
        if not evt.isAccepted():
            super(WebBrowserView, self).dragMoveEvent(evt)
    
    def dropEvent(self, evt):
        """
        Protected method called by a drop event.
        
        @param evt reference to the drop event (QDropEvent)
        """
        super(WebBrowserView, self).dropEvent(evt)
        if not evt.isAccepted() and \
           evt.source() != self and \
           evt.possibleActions() & Qt.CopyAction:
            url = QUrl()
            if len(evt.mimeData().urls()) > 0:
                url = evt.mimeData().urls()[0]
            if not url.isValid():
                url = QUrl(evt.mimeData().text())
            if url.isValid():
                self.setSource(url)
                evt.acceptProposedAction()
    
    def _mousePressEvent(self, evt):
        """
        Protected method called by a mouse press event.
        
        @param evt reference to the mouse event (QMouseEvent)
        """
        self.__mw.setEventMouseButtons(evt.buttons())
        self.__mw.setEventKeyboardModifiers(evt.modifiers())
        
        if evt.button() == Qt.XButton1:
            self.pageAction(QWebEnginePage.Back).trigger()
        elif evt.button() == Qt.XButton2:
            self.pageAction(QWebEnginePage.Forward).trigger()
        else:
            super(WebBrowserView, self).mousePressEvent(evt)
    
    def _mouseReleaseEvent(self, evt):
        """
        Protected method called by a mouse release event.
        
        @param evt reference to the mouse event (QMouseEvent)
        """
        accepted = evt.isAccepted()
        self.__page.event(evt)
        if not evt.isAccepted() and \
           self.__mw.eventMouseButtons() & Qt.MidButton:
            url = QUrl(QApplication.clipboard().text(QClipboard.Selection))
            if not url.isEmpty() and \
               url.isValid() and \
               url.scheme() != "":
                self.__mw.setEventMouseButtons(Qt.NoButton)
                self.__mw.setEventKeyboardModifiers(Qt.NoModifier)
                self.setSource(url)
        evt.setAccepted(accepted)
    
    def _wheelEvent(self, evt):
        """
        Protected method to handle wheel events.
        
        @param evt reference to the wheel event (QWheelEvent)
        """
        delta = evt.angleDelta().y()
        if evt.modifiers() & Qt.ControlModifier:
            if delta < 0:
                self.zoomOut()
            else:
                self.zoomIn()
            evt.accept()
            return
        
        if evt.modifiers() & Qt.ShiftModifier:
            if delta < 0:
                self.backward()
            else:
                self.forward()
            evt.accept()
            return
        
        super(WebBrowserView, self).wheelEvent(evt)
    
    def _keyPressEvent(self, evt):
        """
        Protected method called by a key press.
        
        @param evt reference to the key event (QKeyEvent)
        """
        # TODO: PIM
##        if self.__mw.personalInformationManager().viewKeyPressEvent(self, evt):
##            return
        
        # TODO: Access Keys
##        if self.__enableAccessKeys:
##            self.__accessKeysPressed = (
##                evt.modifiers() == Qt.ControlModifier and
##                evt.key() == Qt.Key_Control)
##            if not self.__accessKeysPressed:
##                if self.__checkForAccessKey(evt):
##                    self.__hideAccessKeys()
##                    evt.accept()
##                    return
##                self.__hideAccessKeys()
##            else:
##                QTimer.singleShot(300, self.__accessKeyShortcut)
        
        self.__ctrlPressed = (evt.key() == Qt.Key_Control)
        super(WebBrowserView, self).keyPressEvent(evt)
    
    def _keyReleaseEvent(self, evt):
        """
        Protected method called by a key release.
        
        @param evt reference to the key event (QKeyEvent)
        """
        # TODO: Access Keys
##        if self.__enableAccessKeys:
##            self.__accessKeysPressed = evt.key() == Qt.Key_Control
        
        self.__ctrlPressed = False
        super(WebBrowserView, self).keyReleaseEvent(evt)
    
    def focusOutEvent(self, evt):
        """
        Protected method called by a focus out event.
        
        @param evt reference to the focus event (QFocusEvent)
        """
        # TODO: Access Keys
##        if self.__accessKeysPressed:
##            self.__hideAccessKeys()
##            self.__accessKeysPressed = False
        
        super(WebBrowserView, self).focusOutEvent(evt)
    
    # TODO: Obsoleted by eventFilter() (?)
##    def event(self, evt):
##        """
##        Public method handling events.
##        
##        @param evt reference to the event (QEvent)
##        @return flag indicating, if the event was handled (boolean)
##        """
##        if evt.type() == QEvent.Gesture:
##            self.gestureEvent(evt)
##            return True
##        
##        return super(WebBrowserView, self).event(evt)
    
    def _gestureEvent(self, evt):
        """
        Protected method handling gesture events.
        
        @param evt reference to the gesture event (QGestureEvent
        """
        pinch = evt.gesture(Qt.PinchGesture)
        if pinch:
            if pinch.state() == Qt.GestureStarted:
                pinch.setScaleFactor(self.__currentZoom / 100.0)
            else:
                scaleFactor = pinch.scaleFactor()
                self.__currentZoom = int(scaleFactor * 100)
                self.__applyZoom()
            evt.accept()
    
    def eventFilter(self, obj, evt):
        """
        Protected method to process event for other objects.
        
        @param obj reference to object to process events for
        @type QObject
        @param evt reference to event to be processed
        @type QEvent
        @return flag indicating that the event should be filtered out
        @rtype bool
        """
        # find the render widget receiving events for the web page
        if obj is self and evt.type() == QEvent.ChildAdded:
            child = evt.child()
            if child and child.inherits(
                    "QtWebEngineCore::RenderWidgetHostViewQtDelegateWidget"):
                self.__rwhvqt = child
                self.__rwhvqt.installEventFilter(self)
        
        # forward events to WebBrowserView
        if obj is self.__rwhvqt:
            wasAccepted = evt.isAccepted()
            evt.setAccepted(False)
            if evt.type() == QEvent.KeyPress:
                self._keyPressEvent(evt)
            elif evt.type() == QEvent.KeyRelease:
                self._keyReleaseEvent(evt)
            elif evt.type() == QEvent.MouseButtonPress:
                self._mousePressEvent(evt)
            elif evt.type() == QEvent.MouseButtonRelease:
                self._mouseReleaseEvent(evt)
##            elif evt.type() == QEvent.MouseMove:
##                self.__mouseMoveEvent(evt)
            elif evt.type() == QEvent.Wheel:
                self._wheelEvent(evt)
            elif evt.type() == QEvent.Gesture:
                self._gestureEvent(evt)
            ret = evt.isAccepted()
            evt.setAccepted(wasAccepted)
            return ret
        
        # block already handled events
        if obj is self:
            if evt.type() in [QEvent.KeyPress, QEvent.KeyRelease,
                              QEvent.MouseButtonPress,
                              QEvent.MouseButtonRelease,
##                              QEvent.MouseMove,
                              QEvent.Wheel, QEvent.Gesture]:
                return True
        
        return super(WebBrowserView, self).eventFilter(obj, evt)
    
    def clearHistory(self):
        """
        Public slot to clear the history.
        """
        self.history().clear()
        self.__urlChanged(self.history().currentItem().url())
    
    ###########################################################################
    ## Signal converters below
    ###########################################################################
    
    def __urlChanged(self, url):
        """
        Private slot to handle the urlChanged signal.
        
        @param url the new url (QUrl)
        """
        self.sourceChanged.emit(url)
        
        self.forwardAvailable.emit(self.isForwardAvailable())
        self.backwardAvailable.emit(self.isBackwardAvailable())
    
##    def __statusBarMessage(self, text):
##        """
##        Private slot to handle the statusBarMessage signal.
##        
##        @param text text to be shown in the status bar (string)
##        """
##        self.__mw.statusBar().showMessage(text)
##    
    def __linkHovered(self, link):
        """
        Private slot to handle the linkHovered signal.
        
        @param link the URL of the link (string)
        """
        self.highlighted.emit(link)
    
    ###########################################################################
    ## Signal handlers below
    ###########################################################################
    
    def __loadStarted(self):
        """
        Private method to handle the loadStarted signal.
        """
        self.__isLoading = True
        self.__progress = 0
    
    def __loadProgress(self, progress):
        """
        Private method to handle the loadProgress signal.
        
        @param progress progress value (integer)
        """
        self.__progress = progress
    
    def __loadFinished(self, ok):
        """
        Private method to handle the loadFinished signal.
        
        @param ok flag indicating the result (boolean)
        """
        self.__isLoading = False
        self.__progress = 0
        
        # TODO: ClickToFlash (?)
##        if Preferences.getHelp("ClickToFlashEnabled"):
##            # this is a hack to make the ClickToFlash button appear
##            self.zoomIn()
##            self.zoomOut()
        
        # TODO: Zoom Manager
##        zoomValue = Helpviewer.HelpWindow.HelpWindow.zoomManager()\
##            .zoomValue(self.url())
##        self.setZoomValue(zoomValue)
        
        if ok:
            pass
            # TODO: AdBlock
##            self.__mw.adBlockManager().page().hideBlockedPageEntries(self.page())
            # TODO: Password Manager
##            self.__mw.passwordManager().fill(self.page())
    
    def isLoading(self):
        """
        Public method to get the loading state.
        
        @return flag indicating the loading state (boolean)
        """
        return self.__isLoading
    
    def progress(self):
        """
        Public method to get the load progress.
        
        @return load progress (integer)
        """
        return self.__progress
    
##    def saveAs(self):
##        """
##        Public method to save the current page to a file.
##        """
##        url = self.url()
##        if url.isEmpty():
##            return
##        
##        self.__mw.downloadManager().download(url, True, mainWindow=self.__mw)
    
##    def __unsupportedContent(self, reply, requestFilename=None,
##                             download=False):
##        """
##        Private slot to handle the unsupportedContent signal.
##        
##        @param reply reference to the reply object (QNetworkReply)
##        @keyparam requestFilename indicating to ask for a filename
##            (boolean or None). If it is None, the behavior is determined
##            by a configuration option.
##        @keyparam download flag indicating a download operation (boolean)
##        """
##        if reply is None:
##            return
##        
##        replyUrl = reply.url()
##        
##        if replyUrl.scheme() == "abp":
##            return
##        
##        if reply.error() == QNetworkReply.NoError:
##            if reply.header(QNetworkRequest.ContentTypeHeader):
##                self.__mw.downloadManager().handleUnsupportedContent(
##                    reply, webPage=self.page(), mainWindow=self.__mw)
##                return
##        
##        replyUrl = reply.url()
##        if replyUrl.isEmpty():
##            return
##        
##        notFoundFrame = self.page().mainFrame()
##        if notFoundFrame is None:
##            return
##        
##        if reply.header(QNetworkRequest.ContentTypeHeader):
##            data = reply.readAll()
##            if contentSniff(data):
##                notFoundFrame.setHtml(str(data, encoding="utf-8"), replyUrl)
##                return
##        
##        urlString = bytes(replyUrl.toEncoded()).decode()
##        title = self.tr("Error loading page: {0}").format(urlString)
##        htmlFile = QFile(":/html/notFoundPage.html")
##        htmlFile.open(QFile.ReadOnly)
##        html = htmlFile.readAll()
##        pixmap = qApp.style()\
##            .standardIcon(QStyle.SP_MessageBoxWarning).pixmap(48, 48)
##        imageBuffer = QBuffer()
##        imageBuffer.open(QIODevice.ReadWrite)
##        if pixmap.save(imageBuffer, "PNG"):
##            html = html.replace("@IMAGE@", imageBuffer.buffer().toBase64())
##        pixmap = qApp.style()\
##            .standardIcon(QStyle.SP_MessageBoxWarning).pixmap(16, 16)
##        imageBuffer = QBuffer()
##        imageBuffer.open(QIODevice.ReadWrite)
##        if pixmap.save(imageBuffer, "PNG"):
##            html = html.replace("@FAVICON@", imageBuffer.buffer().toBase64())
##        html = html.replace("@TITLE@", title.encode("utf8"))
##        html = html.replace("@H1@", reply.errorString().encode("utf8"))
##        html = html.replace(
##            "@H2@", self.tr("When connecting to: {0}.")
##            .format(urlString).encode("utf8"))
##        html = html.replace(
##            "@LI-1@",
##            self.tr("Check the address for errors such as "
##                    "<b>ww</b>.example.org instead of "
##                    "<b>www</b>.example.org").encode("utf8"))
##        html = html.replace(
##            "@LI-2@",
##            self.tr("If the address is correct, try checking the network "
##                    "connection.").encode("utf8"))
##        html = html.replace(
##            "@LI-3@",
##            self.tr(
##                "If your computer or network is protected by a firewall "
##                "or proxy, make sure that the browser is permitted to "
##                "access the network.").encode("utf8"))
##        html = html.replace(
##            "@LI-4@",
##            self.tr("If your cache policy is set to offline browsing,"
##                    "only pages in the local cache are available.")
##            .encode("utf8"))
##        html = html.replace(
##            "@BUTTON@", self.tr("Try Again").encode("utf8"))
##        notFoundFrame.setHtml(bytes(html).decode("utf8"), replyUrl)
##        self.__mw.historyManager().removeHistoryEntry(replyUrl, self.title())
##        self.loadFinished.emit(False)
##    
    
##    def __databaseQuotaExceeded(self, frame, databaseName):
##        """
##        Private slot to handle the case, where the database quota is exceeded.
##        
##        @param frame reference to the frame (QWebFrame)
##        @param databaseName name of the web database (string)
##        """
##        securityOrigin = frame.securityOrigin()
##        if securityOrigin.databaseQuota() > 0 and \
##           securityOrigin.databaseUsage() == 0:
##            # cope with a strange behavior of Qt 4.6, if a database is
##            # accessed for the first time
##            return
##        
##        res = E5MessageBox.yesNo(
##            self,
##            self.tr("Web Database Quota"),
##            self.tr(
##                """<p>The database quota of <strong>{0}</strong> has"""
##                """ been exceeded while accessing database <strong>{1}"""
##                """</strong>.</p><p>Shall it be changed?</p>""")
##            .format(self.__dataString(securityOrigin.databaseQuota()),
##                    databaseName),
##            yesDefault=True)
##        if res:
##            newQuota, ok = QInputDialog.getInt(
##                self,
##                self.tr("New Web Database Quota"),
##                self.tr(
##                    "Enter the new quota in MB (current = {0}, used = {1}; "
##                    "step size = 5 MB):"
##                    .format(
##                        self.__dataString(securityOrigin.databaseQuota()),
##                        self.__dataString(securityOrigin.databaseUsage()))),
##                securityOrigin.databaseQuota() // (1024 * 1024),
##                0, 2147483647, 5)
##            if ok:
##                securityOrigin.setDatabaseQuota(newQuota * 1024 * 1024)
##    
##    def __dataString(self, size):
##        """
##        Private method to generate a formatted data string.
##        
##        @param size size to be formatted (integer)
##        @return formatted data string (string)
##        """
##        unit = ""
##        if size < 1024:
##            unit = self.tr("bytes")
##        elif size < 1024 * 1024:
##            size /= 1024
##            unit = self.tr("kB")
##        else:
##            size /= 1024 * 1024
##            unit = self.tr("MB")
##        return "{0:.1f} {1}".format(size, unit)
    
    ###########################################################################
    ## Access key related methods below
    ###########################################################################
    
    # TODO: Access Keys
##    def __accessKeyShortcut(self):
##        """
##        Private slot to switch the display of access keys.
##        """
##        if not self.hasFocus() or \
##           not self.__accessKeysPressed or \
##           not self.__enableAccessKeys:
##            return
##        
##        if self.__accessKeyLabels:
##            self.__hideAccessKeys()
##        else:
##            self.__showAccessKeys()
##        
##        self.__accessKeysPressed = False
##    
##    def __checkForAccessKey(self, evt):
##        """
##        Private method to check the existence of an access key and activate the
##        corresponding link.
##        
##        @param evt reference to the key event (QKeyEvent)
##        @return flag indicating, if the event was handled (boolean)
##        """
##        if not self.__accessKeyLabels:
##            return False
##        
##        text = evt.text()
##        if not text:
##            return False
##        
##        key = text[0].upper()
##        handled = False
##        if key in self.__accessKeyNodes:
##            element = self.__accessKeyNodes[key]
##            p = element.geometry().center()
##            frame = element.webFrame()
##            p -= frame.scrollPosition()
##            frame = frame.parentFrame()
##            while frame and frame != self.page().mainFrame():
##                p -= frame.scrollPosition()
##                frame = frame.parentFrame()
##            pevent = QMouseEvent(
##                QEvent.MouseButtonPress, p, Qt.LeftButton,
##                Qt.MouseButtons(Qt.NoButton),
##                Qt.KeyboardModifiers(Qt.NoModifier))
##            qApp.sendEvent(self, pevent)
##            revent = QMouseEvent(
##                QEvent.MouseButtonRelease, p, Qt.LeftButton,
##                Qt.MouseButtons(Qt.NoButton),
##                Qt.KeyboardModifiers(Qt.NoModifier))
##            qApp.sendEvent(self, revent)
##            handled = True
##        
##        return handled
##    
##    def __hideAccessKeys(self):
##        """
##        Private slot to hide the access key labels.
##        """
##        if self.__accessKeyLabels:
##            for label in self.__accessKeyLabels:
##                label.hide()
##                label.deleteLater()
##            self.__accessKeyLabels = []
##            self.__accessKeyNodes = {}
##            self.update()
##    
##    def __showAccessKeys(self):
##        """
##        Private method to show the access key labels.
##        """
##        supportedElements = [
##            "input", "a", "area", "button", "label", "legend", "textarea",
##        ]
##        unusedKeys = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z" \
##            " 0 1 2 3 4 5 6 7 8 9".split()
##        
##        viewport = QRect(self.__page.mainFrame().scrollPosition(),
##                         self.__page.viewportSize())
##        # Priority first goes to elements with accesskey attributes
##        alreadyLabeled = []
##        for elementType in supportedElements:
##            result = self.page().mainFrame().findAllElements(elementType)\
##                .toList()
##            for element in result:
##                geometry = element.geometry()
##                if geometry.size().isEmpty() or \
##                   not viewport.contains(geometry.topLeft()):
##                    continue
##                
##                accessKeyAttribute = element.attribute("accesskey").upper()
##                if not accessKeyAttribute:
##                    continue
##                
##                accessKey = ""
##                i = 0
##                while i < len(accessKeyAttribute):
##                    if accessKeyAttribute[i] in unusedKeys:
##                        accessKey = accessKeyAttribute[i]
##                        break
##                    i += 2
##                if accessKey == "":
##                    continue
##                unusedKeys.remove(accessKey)
##                self.__makeAccessLabel(accessKey, element)
##                alreadyLabeled.append(element)
##        
##        # Pick an access key first from the letters in the text and then
##        # from the list of unused access keys
##        for elementType in supportedElements:
##            result = self.page().mainFrame().findAllElements(elementType)\
##                .toList()
##            for element in result:
##                geometry = element.geometry()
##                if not unusedKeys or \
##                   element in alreadyLabeled or \
##                   geometry.size().isEmpty() or \
##                   not viewport.contains(geometry.topLeft()):
##                    continue
##                
##                accessKey = ""
##                text = element.toPlainText().upper()
##                for c in text:
##                    if c in unusedKeys:
##                        accessKey = c
##                        break
##                if accessKey == "":
##                    accessKey = unusedKeys[0]
##                unusedKeys.remove(accessKey)
##                self.__makeAccessLabel(accessKey, element)
##    
##    def __makeAccessLabel(self, accessKey, element):
##        """
##        Private method to generate the access label for an element.
##        
##        @param accessKey access key to generate the label for (str)
##        @param element reference to the web element to create the label for
##            (QWebElement)
##        """
##        label = QLabel(self)
##        label.setText("<qt><b>{0}</b></qt>".format(accessKey))
##        
##        p = QToolTip.palette()
##        color = QColor(Qt.yellow).lighter(150)
##        color.setAlpha(175)
##        p.setColor(QPalette.Window, color)
##        label.setPalette(p)
##        label.setAutoFillBackground(True)
##        label.setFrameStyle(QFrame.Box | QFrame.Plain)
##        point = element.geometry().center()
##        point -= self.__page.mainFrame().scrollPosition()
##        label.move(point)
##        label.show()
##        point.setX(point.x() - label.width() // 2)
##        label.move(point)
##        self.__accessKeyLabels.append(label)
##        self.__accessKeyNodes[accessKey] = element
    
    ###########################################################################
    ## Miscellaneous methods below
    ###########################################################################
    
    # TODO: check, if this is needed (referenced anywhere) (same for HelpBrowserWV)
    def createWindow(self, windowType):
        """
        Public method called, when a new window should be created.
        
        @param windowType type of the requested window (QWebPage.WebWindowType)
        @return reference to the created browser window (HelpBrowser)
        """
        self.__mw.newTab(addNextTo=self)
        return self.__mw.currentBrowser()
    
    def preferencesChanged(self):
        """
        Public method to indicate a change of the settings.
        """
        # TODO: Access Keys
##        self.__enableAccessKeys = Preferences.getHelp("AccessKeysEnabled")
##        if not self.__enableAccessKeys:
##            self.__hideAccessKeys()
        
        self.reload()
    
    ###########################################################################
    ## RSS related methods below
    ###########################################################################
    
    # TODO: RSS, extract links from page to implement RSS stuff
##    def checkRSS(self):
##        """
##        Public method to check, if the loaded page contains feed links.
##        
##        @return flag indicating the existence of feed links (boolean)
##        """
##        self.__rss = []
##        
##        frame = self.page()
##        linkElementsList = frame.findAllElements("link").toList()
##        
##        for linkElement in linkElementsList:
##            # only atom+xml and rss+xml will be processed
##            if linkElement.attribute("rel") != "alternate" or \
##               (linkElement.attribute("type") != "application/rss+xml" and
##                    linkElement.attribute("type") != "application/atom+xml"):
##                continue
##            
##            title = linkElement.attribute("title")
##            href = linkElement.attribute("href")
##            if href == "" or title == "":
##                continue
##            self.__rss.append((title, href))
##        
##        return len(self.__rss) > 0
    
    def getRSS(self):
        """
        Public method to get the extracted RSS feeds.
        
        @return list of RSS feeds (list of tuples of two strings)
        """
        return self.__rss
    
    def hasRSS(self):
        """
        Public method to check, if the loaded page has RSS links.
        
        @return flag indicating the presence of RSS links (boolean)
        """
        return len(self.__rss) > 0
    
    ###########################################################################
    ## Clicked Frame slots
    ###########################################################################
    
##    def __loadClickedFrame(self):
##        """
##        Private slot to load the selected frame only.
##        """
##        self.setSource(self.__clickedFrame.url())
##    
##    def __printClickedFrame(self):
##        """
##        Private slot to print the selected frame.
##        """
##        printer = QPrinter(mode=QPrinter.HighResolution)
##        if Preferences.getPrinter("ColorMode"):
##            printer.setColorMode(QPrinter.Color)
##        else:
##            printer.setColorMode(QPrinter.GrayScale)
##        if Preferences.getPrinter("FirstPageFirst"):
##            printer.setPageOrder(QPrinter.FirstPageFirst)
##        else:
##            printer.setPageOrder(QPrinter.LastPageFirst)
##        printer.setPageMargins(
##            Preferences.getPrinter("LeftMargin") * 10,
##            Preferences.getPrinter("TopMargin") * 10,
##            Preferences.getPrinter("RightMargin") * 10,
##            Preferences.getPrinter("BottomMargin") * 10,
##            QPrinter.Millimeter
##        )
##        printerName = Preferences.getPrinter("PrinterName")
##        if printerName:
##            printer.setPrinterName(printerName)
##        
##        printDialog = QPrintDialog(printer, self)
##        if printDialog.exec_() == QDialog.Accepted:
##            try:
##                self.__clickedFrame.print_(printer)
##            except AttributeError:
##                E5MessageBox.critical(
##                    self,
##                    self.tr("eric6 Web Browser"),
##                    self.tr(
##                        """<p>Printing is not available due to a bug in"""
##                        """ PyQt5. Please upgrade.</p>"""))
##    
##    def __printPreviewClickedFrame(self):
##        """
##        Private slot to show a print preview of the clicked frame.
##        """
##        from PyQt5.QtPrintSupport import QPrintPreviewDialog
##        
##        printer = QPrinter(mode=QPrinter.HighResolution)
##        if Preferences.getPrinter("ColorMode"):
##            printer.setColorMode(QPrinter.Color)
##        else:
##            printer.setColorMode(QPrinter.GrayScale)
##        if Preferences.getPrinter("FirstPageFirst"):
##            printer.setPageOrder(QPrinter.FirstPageFirst)
##        else:
##            printer.setPageOrder(QPrinter.LastPageFirst)
##        printer.setPageMargins(
##            Preferences.getPrinter("LeftMargin") * 10,
##            Preferences.getPrinter("TopMargin") * 10,
##            Preferences.getPrinter("RightMargin") * 10,
##            Preferences.getPrinter("BottomMargin") * 10,
##            QPrinter.Millimeter
##        )
##        printerName = Preferences.getPrinter("PrinterName")
##        if printerName:
##            printer.setPrinterName(printerName)
##        
##        preview = QPrintPreviewDialog(printer, self)
##        preview.paintRequested.connect(self.__generatePrintPreviewClickedFrame)
##        preview.exec_()
##    
##    def __generatePrintPreviewClickedFrame(self, printer):
##        """
##        Private slot to generate a print preview of the clicked frame.
##        
##        @param printer reference to the printer object (QPrinter)
##        """
##        try:
##            self.__clickedFrame.print_(printer)
##        except AttributeError:
##            E5MessageBox.critical(
##                self,
##                self.tr("eric6 Web Browser"),
##                self.tr(
##                    """<p>Printing is not available due to a bug in PyQt5."""
##                    """Please upgrade.</p>"""))
##            return
##    
##    def __printPdfClickedFrame(self):
##        """
##        Private slot to print the selected frame to PDF.
##        """
##        printer = QPrinter(mode=QPrinter.HighResolution)
##        if Preferences.getPrinter("ColorMode"):
##            printer.setColorMode(QPrinter.Color)
##        else:
##            printer.setColorMode(QPrinter.GrayScale)
##        printerName = Preferences.getPrinter("PrinterName")
##        if printerName:
##            printer.setPrinterName(printerName)
##        printer.setOutputFormat(QPrinter.PdfFormat)
##        name = self.__clickedFrame.url().path().rsplit('/', 1)[-1]
##        if name:
##            name = name.rsplit('.', 1)[0]
##            name += '.pdf'
##            printer.setOutputFileName(name)
##        
##        printDialog = QPrintDialog(printer, self)
##        if printDialog.exec_() == QDialog.Accepted:
##            try:
##                self.__clickedFrame.print_(printer)
##            except AttributeError:
##                E5MessageBox.critical(
##                    self,
##                    self.tr("eric6 Web Browser"),
##                    self.tr(
##                        """<p>Printing is not available due to a bug in"""
##                        """ PyQt5. Please upgrade.</p>"""))
##                return
##    
##    def __zoomInClickedFrame(self):
##        """
##        Private slot to zoom into the clicked frame.
##        """
##        index = self.__levelForZoom(
##            int(self.__clickedFrame.zoomFactor() * 100))
##        if index < len(self.__zoomLevels) - 1:
##            self.__clickedFrame.setZoomFactor(
##                self.__zoomLevels[index + 1] / 100)
##    
##    def __zoomResetClickedFrame(self):
##        """
##        Private slot to reset the zoom factor of the clicked frame.
##        """
##        self.__clickedFrame.setZoomFactor(self.__currentZoom / 100)
##    
##    def __zoomOutClickedFrame(self):
##        """
##        Private slot to zoom out of the clicked frame.
##        """
##        index = self.__levelForZoom(
##            int(self.__clickedFrame.zoomFactor() * 100))
##        if index > 0:
##            self.__clickedFrame.setZoomFactor(
##                self.__zoomLevels[index - 1] / 100)
##    
##    def __showClickedFrameSource(self):
##        """
##        Private slot to show the source of the clicked frame.
##        """
##        from QScintilla.MiniEditor import MiniEditor
##        src = self.__clickedFrame.toHtml()
##        editor = MiniEditor(parent=self)
##        editor.setText(src, "Html")
##        editor.setLanguage("dummy.html")
##        editor.show()


##def contentSniff(data):
##    """
##    Module function to do some content sniffing to check, if the data is HTML.
##    
##    @param data data block to sniff at (string)
##    @return flag indicating HTML content (boolean)
##    """
##    if data.contains("<!doctype") or \
##       data.contains("<script") or \
##       data.contains("<html") or \
##       data.contains("<!--") or \
##       data.contains("<head") or \
##       data.contains("<iframe") or \
##       data.contains("<h1") or \
##       data.contains("<div") or \
##       data.contains("<font") or \
##       data.contains("<table") or \
##       data.contains("<a") or \
##       data.contains("<style") or \
##       data.contains("<title") or \
##       data.contains("<b") or \
##       data.contains("<body") or \
##       data.contains("<br") or \
##       data.contains("<p"):
##        return True
##    
##    return False
