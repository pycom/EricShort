# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the GreaseMonkey script.
"""

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QUrl, QRegExp, \
    QByteArray,  QCryptographicHash
from PyQt5.QtWebEngineWidgets import QWebEngineScript

from .GreaseMonkeyUrlMatcher import GreaseMonkeyUrlMatcher
from .GreaseMonkeyJavaScript import bootstrap_js, values_js

from ..Tools.DelayedFileWatcher import DelayedFileWatcher


class GreaseMonkeyScript(QObject):
    """
    Class implementing the GreaseMonkey script.
    """
    DocumentStart = 0
    DocumentEnd = 1
    
    scriptChanged = pyqtSignal()
    
    def __init__(self, manager, path):
        """
        Constructor
        
        @param manager reference to the manager object (GreaseMonkeyManager)
        @param path path of the Javascript file (string)
        """
        super(GreaseMonkeyScript, self).__init__(manager)
        
        self.__manager = manager
        self.__fileWatcher = DelayedFileWatcher(parent=None)
        
        self.__name = ""
        self.__namespace = "GreaseMonkeyNS"
        self.__description = ""
        self.__version = ""
        
        self.__include = []
        self.__exclude = []
        
        self.__downloadUrl = QUrl()
        self.__updateUrl = QUrl()
        self.__startAt = GreaseMonkeyScript.DocumentEnd
        
        self.__script = ""
        self.__fileName = path
        self.__enabled = True
        self.__valid = False
        self.__metaData = ""
        self.__noFrames = False
        
        self.__parseScript()
        
        self.__fileWatcher.delayedFileChanged.connect(
            self.__watchedFileChanged)
    
    def isValid(self):
        """
        Public method to check the validity of the script.
        
        @return flag indicating a valid script (boolean)
        """
        return self.__valid
    
    def name(self):
        """
        Public method to get the name of the script.
        
        @return name of the script (string)
        """
        return self.__name
    
    def nameSpace(self):
        """
        Public method to get the name space of the script.
        
        @return name space of the script (string)
        """
        return self.__namespace
    
    def fullName(self):
        """
        Public method to get the full name of the script.
        
        @return full name of the script (string)
        """
        return "{0}/{1}".format(self.__namespace, self.__name)
    
    def description(self):
        """
        Public method to get the description of the script.
        
        @return description of the script (string)
        """
        return self.__description
    
    def version(self):
        """
        Public method to get the version of the script.
        
        @return version of the script (string)
        """
        return self.__version
    
    def downloadUrl(self):
        """
        Public method to get the download URL of the script.
        
        @return download URL of the script (QUrl)
        """
        return QUrl(self.__downloadUrl)
    
    def updateUrl(self):
        """
        Public method to get the update URL of the script.
        
        @return update URL of the script (QUrl)
        """
        return QUrl(self.__updateUrl)
    
    def startAt(self):
        """
        Public method to get the start point of the script.
        
        @return start point of the script (DocumentStart or DocumentEnd)
        """
        return self.__startAt
    
    def noFrames(self):
        """
        Public method to get the noFrames flag.
        
        @return flag indicating to not run on sub frames
        @rtype bool
        """
        return self.__noFrames
    
    def isEnabled(self):
        """
        Public method to check, if the script is enabled.
        
        @return flag indicating an enabled state (boolean)
        """
        return self.__enabled and self.__valid
    
    def setEnabled(self, enable):
        """
        Public method to enable a script.
        
        @param enable flag indicating the new enabled state (boolean)
        """
        self.__enabled = enable
    
    def include(self):
        """
        Public method to get the list of included URLs.
        
        @return list of included URLs (list of strings)
        """
        list = []
        for matcher in self.__include:
            list.append(matcher.pattern())
        return list
    
    def exclude(self):
        """
        Public method to get the list of excluded URLs.
        
        @return list of excluded URLs (list of strings)
        """
        list = []
        for matcher in self.__exclude:
            list.append(matcher.pattern())
        return list
    
    def script(self):
        """
        Public method to get the Javascript source.
        
        @return Javascript source (string)
        """
        return self.__script
    
    def metaData(self):
        """
        Public method to get the script meta information.
        
        @return script meta information
        @rtype str
        """
        return self.__metaData
    
    def fileName(self):
        """
        Public method to get the path of the Javascript file.
        
        @return path path of the Javascript file (string)
        """
        return self.__fileName
    
    def match(self, urlString):
        """
        Public method to check, if the script matches the given URL.
        
        @param urlString URL (string)
        @return flag indicating a match (boolean)
        """
        if not self.isEnabled():
            return False
        
        for matcher in self.__exclude:
            if matcher.match(urlString):
                return False
        
        for matcher in self.__include:
            if matcher.match(urlString):
                return True
        
        return False
    
    @pyqtSlot(str)
    def __watchedFileChanged(self, fileName):
        """
        Private slot handling changes of the script file.
        
        @param fileName path of the script file
        @type str
        """
        if self.__fileName == fileName:
            self.__parseScript()
            
            self.__manager.removeScript(self, False)
            self.__manager.addScript(self)
            
            self.scriptChanged.emit()
    
    def __parseScript(self, path):
        """
        Private method to parse the given script and populate the data
        structure.
        
        @param path path of the Javascript file (string)
        """
        self.__name = ""
        self.__namespace = "GreaseMonkeyNS"
        self.__description = ""
        self.__version = ""
        
        self.__include = []
        self.__exclude = []
        
        self.__downloadUrl = QUrl()
        self.__updateUrl = QUrl()
        self.__startAt = GreaseMonkeyScript.DocumentEnd
        
        self.__script = ""
        self.__enabled = True
        self.__valid = False
        self.__metaData = ""
        self.__noFrames = False
        
        try:
            f = open(path, "r", encoding="utf-8")
            fileData = f.read()
            f.close()
        except (IOError, OSError):
            # silently ignore because it shouldn't happen
            return
        
        if self.__fileName not in self.__fileWatcher.files():
            self.__fileWatcher.addPath(self.__fileName)
        
        rx = QRegExp("// ==UserScript==(.*)// ==/UserScript==")
        rx.indexIn(fileData)
        metaDataBlock = rx.cap(1).strip()
        
        if metaDataBlock == "":
            # invalid script file
            return
        
        requireList = []
        for line in metaDataBlock.splitlines():
            if not line.strip():
                continue
            
            if not line.startswith("// @"):
                continue
            
            line = line[3:].replace("\t", " ")
            index = line.find(" ")
            if index < 0:
                continue
            
            key = line[:index].strip()
            value = line[index + 1:].strip()
            
            # Ignored values: @resource, @unwrap
            
            if not key or not value:
                continue
            
            if key == "@name":
                self.__name = value
            
            elif key == "@namespace":
                self.__namespace = value
            
            elif key == "@description":
                self.__description = value
            
            elif key == "@version":
                self.__version = value
            
##            elif key == "@updateURL":
##                self.__downloadUrl = QUrl(value)
##            
            elif key in ["@include", "@match"]:
                self.__include.append(GreaseMonkeyUrlMatcher(value))
            
            elif key in ["@exclude", "@exclude_match"]:
                self.__exclude.append(GreaseMonkeyUrlMatcher(value))
            
            elif key == "@require":
                requireList.append(value)
            
            elif key == "@run-at":
                if value == "document-end":
                    self.__startAt = GreaseMonkeyScript.DocumentEnd
                elif value == "document-start":
                    self.__startAt = GreaseMonkeyScript.DocumentStart
            
            elif key == "@downloadURL" and self.__downloadUrl.isEmpty():
                self.__downloadUrl = QUrl(value)
            
            elif key == "@updateURL" and self.__updateUrl.isEmpty():
                self.__updateUrl = QUrl(value)
        
        if not self.__include:
            self.__include.append(GreaseMonkeyUrlMatcher("*"))
        
        marker = "// ==/UserScript=="
        index = fileData.find(marker) + len(marker)
        self.__metaData = fileData[:index]
        script = fileData[index:].strip()
        
        nspace = bytes(QCryptographicHash.hash(
            QByteArray(self.fullName().encode("utf-8")),
            QCryptographicHash.Md4).toHex()).decode("ascii")
        valuesScript = values_js.format(nspace)
        self.__script = "(function(){{{0}\n{1}\n{2}\n}})();".format(
            valuesScript, self.__manager.requireScripts(requireList), script
        )
        self.__valid = True
    
    def webScript(self):
        """
        Public method to create a script object.
        
        @return prepared script object
        @rtype QWebEngineScript
        """
        script = QWebEngineScript()
        script.setName(self.fullName())
        if self.startAt() == GreaseMonkeyScript.DocumentStart:
            script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        else:
            script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(not self.__noFrames)
        script.setSourceCode("{0}\n{1}\n{2}".format(
            self.__metaData, bootstrap_js, self.__script
        ))
        return script
