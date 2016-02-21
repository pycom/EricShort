# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing tool functions for the web browser.
"""

from __future__ import unicode_literals
try:
    str = unicode       # __IGNORE_EXCEPTION__
except NameError:
    pass

import os

from PyQt5.QtCore import QFile, QByteArray, QUrl


def readAllFileContents(filename):
    """
    Function to read the string contents of the given file.
    
    @param filename name of the file
    @type str
    @return contents of the file
    @rtype str
    """
    return str(readAllFileByteContents(filename), encoding="utf-8")


def readAllFileByteContents(filename):
    """
    Function to read the bytes contents of the given file.
    
    @param filename name of the file
    @type str
    @return contents of the file
    @rtype str
    """
    dataFile = QFile(filename)
    if filename and dataFile.open(QFile.ReadOnly):
        contents = dataFile.readAll()
        dataFile.close()
        return contents
    
    return QByteArray()


def containsSpace(string):
    """
    Function to check, if a string contains whitespace characters.
    
    @param string string to be checked
    @type str
    @return flag indicating the presence of at least one whitespace character
    @rtype bool
    """
    for ch in string:
        if ch.isspace():
            return True
    
    return False


def ensureUniqueFilename(name, appendFormat="({0})"):
    """
    Module function to generate an unique file name based on a pattern.
    
    @param name desired file name (string)
    @param appendFormat format pattern to be used to make the unique name
        (string)
    @return unique file name
    """
    if not os.path.exists(name):
        return name
    
    tmpFileName = name
    i = 1
    while os.path.exists(tmpFileName):
        tmpFileName = name
        index = tmpFileName.rfind(".")
        
        appendString = appendFormat.format(i)
        if index == -1:
            tmpFileName += appendString
        else:
            tmpFileName = tmpFileName[:index] + appendString + \
                tmpFileName[index:]
        i += 1
    
    return tmpFileName


def getFileNameFromUrl(url):
    """
    Module function to generate a file name based on the given URL.
    
    @param url URL (QUrl)
    @return file name (string)
    """
    fileName = url.toString(QUrl.RemoveFragment | QUrl.RemoveQuery |
                            QUrl.RemoveScheme | QUrl.RemovePort)
    if fileName.find("/") != -1:
        pos = fileName.rfind("/")
        fileName = fileName[pos:]
        fileName = fileName.replace("/", "")
    
    fileName = filterCharsFromFilename(fileName)
    
    if not fileName:
        fileName = filterCharsFromFilename(url.host().replace(".", "_"))
    
    return fileName


def filterCharsFromFilename(name):
    """
    Module function to filter illegal characters.
    
    @param name name to be sanitized (string)
    @return sanitized name (string)
    """
    return name\
        .replace("/", "_")\
        .replace("\\", "")\
        .replace(":", "")\
        .replace("*", "")\
        .replace("?", "")\
        .replace('"', "")\
        .replace("<", "")\
        .replace(">", "")\
        .replace("|", "")
