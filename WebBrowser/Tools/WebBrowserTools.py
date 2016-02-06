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

from PyQt5.QtCore import QFile, QByteArray


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
