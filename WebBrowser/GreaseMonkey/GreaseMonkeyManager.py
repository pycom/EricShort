# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the manager for GreaseMonkey scripts.
"""

from __future__ import unicode_literals

import os

from PyQt5.QtCore import pyqtSignal, QObject, QTimer, QFile, QDir, QSettings, \
    QUrl, QByteArray
from PyQt5.QtNetwork import QNetworkAccessManager

import Utilities
import Preferences

from WebBrowser.WebBrowserWindow import WebBrowserWindow
from .GreaseMonkeyUrlInterceptor import GreaseMonkeyUrlInterceptor


class GreaseMonkeyManager(QObject):
    """
    Class implementing the manager for GreaseMonkey scripts.
    """
    scriptsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        super(GreaseMonkeyManager, self).__init__(parent)
        
        self.__disabledScripts = []
        self.__scripts = []
        self.__downloaders = []
        
        self.__interceptor = GreaseMonkeyUrlInterceptor(self)
        WebBrowserWindow.networkManager().installUrlInterceptor(
            self.__interceptor)
        
        QTimer.singleShot(0, self.__load)
    
    def __del__(self):
        """
        Special method called during object destruction.
        """
        WebBrowserWindow.networkManager().removeUrlInterceptor(
            self.__interceptor)
    
    def showConfigurationDialog(self, parent=None):
        """
        Public method to show the configuration dialog.
        
        @param parent reference to the parent widget (QWidget)
        """
        from .GreaseMonkeyConfiguration.GreaseMonkeyConfigurationDialog \
            import GreaseMonkeyConfigurationDialog
        self.__configDiaolg = GreaseMonkeyConfigurationDialog(self, parent)
        self.__configDiaolg.show()
    
    def downloadScript(self, request):
        """
        Public method to download a GreaseMonkey script.
        
        @param request reference to the request (QNetworkRequest)
        """
        from .GreaseMonkeyDownloader import GreaseMonkeyDownloader
        downloader = GreaseMonkeyDownloader(request, self)
        downloader.finished.connect(self.__downloaderFinished)
        self.__downloaders.append(downloader)
    
    def __downloaderFinished(self):
        """
        Private slot to handle the completion of a script download.
        """
        downloader = self.sender()
        if downloader is None or downloader not in self.__downloaders:
            return
        
        self.__downloaders.remove(downloader)
    
    def scriptsDirectory(self):
        """
        Public method to get the path of the scripts directory.
        
        @return path of the scripts directory (string)
        """
        return os.path.join(
            Utilities.getConfigDir(), "web_browser", "greasemonkey")
    
    def requireScriptsDirectory(self):
        """
        Public method to get the path of the scripts directory.
        
        @return path of the scripts directory (string)
        """
        return os.path.join(self.scriptsDirectory(), "requires")
    
    def requireScripts(self, urlList):
        """
        Public method to get the sources of all required scripts.
        
        @param urlList list of URLs (list of string)
        @return sources of all required scripts (string)
        """
        requiresDir = QDir(self.requireScriptsDirectory())
        if not requiresDir.exists() or len(urlList) == 0:
            return ""
        
        script = ""
        
        settings = QSettings(
            os.path.join(self.requireScriptsDirectory(), "requires.ini"),
            QSettings.IniFormat)
        settings.beginGroup("Files")
        for url in urlList:
            if settings.contains(url):
                fileName = settings.value(url)
                try:
                    f = open(fileName, "r", encoding="utf-8")
                    source = f.read()
                    f.close()
                except (IOError, OSError):
                    source = ""
                script += source.strip() + "\n"
        
        return script
    
    def saveConfiguration(self):
        """
        Public method to save the configuration.
        """
        Preferences.setWebBrowser("GreaseMonkeyDisabledScripts",
                                  self.__disabledScripts)
    
    def allScripts(self):
        """
        Public method to get a list of all scripts.
        
        @return list of all scripts (list of GreaseMonkeyScript)
        """
        return self.__scripts[:]
    
    def containsScript(self, fullName):
        """
        Public method to check, if the given script exists.
        
        @param fullName full name of the script (string)
        @return flag indicating the existence (boolean)
        """
        for script in self.__scripts:
            if script.fullName() == fullName:
                return True
        
        return False
    
    def enableScript(self, script):
        """
        Public method to enable the given script.
        
        @param script script to be enabled (GreaseMonkeyScript)
        """
        script.setEnabled(True)
        fullName = script.fullName()
        if fullName in self.__disabledScripts:
            self.__disabledScripts.remove(fullName)
        
        collection = WebBrowserWindow.webProfile().scripts()
        collection.insert(script.webScript())
    
    def disableScript(self, script):
        """
        Public method to disable the given script.
        
        @param script script to be disabled (GreaseMonkeyScript)
        """
        script.setEnabled(False)
        fullName = script.fullName()
        if fullName not in self.__disabledScripts:
            self.__disabledScripts.append(fullName)
        
        collection = WebBrowserWindow.webProfile().scripts()
        collection.remove(collection.findScript(fullName))
    
    def addScript(self, script):
        """
        Public method to add a script.
        
        @param script script to be added (GreaseMonkeyScript)
        @return flag indicating success (boolean)
        """
        if not script or not script.isValid():
            return False
        
        self.__scripts.append(script)
        script.scriptChanged.connect(self.__scriptChanged)
        
        collection = WebBrowserWindow.webProfile().scripts()
        collection.insert(script.webScript())
        
        self.scriptsChanged.emit()
        return True
    
    def removeScript(self, script, removeFile=True):
        """
        Public method to remove a script.
        
        @param script script to be removed (GreaseMonkeyScript)
        @param removeFile flag indicating to remove the script file as well
            (bool)
        @return flag indicating success (boolean)
        """
        if not script:
            return False
        
        try:
            self.__scripts.remove(script)
        except ValueError:
            pass
        
        fullName = script.fullName()
        collection = WebBrowserWindow.webProfile().scripts()
        collection.remove(collection.findScript(fullName))
        
        if fullName in self.__disabledScripts:
            self.__disabledScripts.remove(fullName)
        
        if removeFile:
            QFile.remove(script.fileName())
            del script
        
        self.scriptsChanged.emit()
        return True
    
    def canRunOnScheme(self, scheme):
        """
        Public method to check, if scripts can be run on a scheme.
        
        @param scheme scheme to check (string)
        @return flag indicating, that scripts can be run (boolean)
        """
        return scheme in ["http", "https", "data", "ftp"]
    
    def __load(self):
        """
        Private slot to load the available scripts into the manager.
        """
        scriptsDir = QDir(self.scriptsDirectory())
        if not scriptsDir.exists():
            scriptsDir.mkpath(self.scriptsDirectory())
        
        if not scriptsDir.exists("requires"):
            scriptsDir.mkdir("requires")
        
        self.__disabledScripts = \
            Preferences.getWebBrowser("GreaseMonkeyDisabledScripts")
        
        from .GreaseMonkeyScript import GreaseMonkeyScript
        for fileName in scriptsDir.entryList(["*.js"], QDir.Files):
            absolutePath = scriptsDir.absoluteFilePath(fileName)
            script = GreaseMonkeyScript(self, absolutePath)
            
            if not script.isValid():
                del script
                continue
            
            self.__scripts.append(script)
            
            if script.fullName() in self.__disabledScripts:
                script.setEnabled(False)
            else:
                collection = WebBrowserWindow.webProfile().scripts()
                collection.insert(script.webScript())
    
    def __scriptChanged(self):
        """
        Private slot handling a changed script.
        """
        script = self.sender()
        if not script:
            return
        
        fullName = script.fullName()
        collection = WebBrowserWindow.webProfile().scripts()
        collection.remove(collection.findScript(fullName))
        collection.insert(script.webScript())
