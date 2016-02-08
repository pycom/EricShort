# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an object for testing certain aspects of a web page.
"""

#
# This code was ported from QupZilla.
# Copyright (C) David Rosca <nowrep@gmail.com>
#

from __future__ import unicode_literals

from PyQt5.QtCore import QPoint, QRect, QUrl

class WebHitTestResult(object):
    """
    Class implementing an object for testing certain aspects of a web page.
    """
    def __init__(self, page, pos):
        """
        Constructor
        
        @param page reference to the web page
        @type WebBrowserPage
        @param pos position to be tested
        @type QPoint
        """
        self.__isNull = True
        self.__isContentEditable = False
        self.__isContentSelected = False
        self.__isMediaPaused = False
        self.__isMediaMuted = False
        self.__pos = QPoint(pos)
        self.__alternateText = ""
        self.__boundingRect = QRect()
        self.__imageUrl = QUrl()
        self.__linkTitle = ""
        self.__linkUrl = QUrl()
        self.__mediaUrl = QUrl()
        self.__tagName = ""
    
        script = """
            (function() {{
                var e = document.elementFromPoint({0}, {1});
                if (!e)
                    return;
                function isMediaElement(e) {{
                    return e.tagName == 'AUDIO' || e.tagName == 'VIDEO';
                }}
                function isEditableElement(e) {{
                    if (e.isContentEditable)
                        return true;
                    if (e.tagName == 'INPUT' || e.tagName == 'TEXTAREA')
                        return e.getAttribute('readonly') != 'readonly';
                    return false;
                }}
                function isSelected(e) {{
                    var selection = window.getSelection();
                    if (selection.type != 'Range')
                        return false;
                    return window.getSelection().containsNode(e, true);
                }}
                var res = {{
                    alternateText: e.getAttribute('alt'),
                    boundingRect: '',
                    imageUrl: '',
                    contentEditable: isEditableElement(e),
                    contentSelected: isSelected(e),
                    linkTitle: '',
                    linkUrl: '',
                    mediaUrl: '',
                    mediaPaused: false,
                    mediaMuted: false,
                    tagName: e.tagName.toLowerCase()
                }};
                var r = e.getBoundingClientRect();
                res.boundingRect = [r.top, r.left, r.width, r.height];
                if (e.tagName == 'IMG')
                    res.imageUrl = e.getAttribute('src');
                if (e.tagName == 'A') {{
                    res.linkTitle = e.text;
                    res.linkUrl = e.getAttribute('href');
                }}
                while (e) {{
                    if (res.linkTitle == '' && e.tagName == 'A')
                        res.linkTitle = e.text;
                    if (res.linkUrl == '' && e.tagName == 'A')
                        res.linkUrl = e.getAttribute('href');
                    if (res.mediaUrl == '' && isMediaElement(e)) {{
                        res.mediaUrl = e.currentSrc;
                        res.mediaPaused = e.paused;
                        res.mediaMuted = e.muted;
                    }}
                    e = e.parentElement;
                }}
                return res;
            }})()
        """.format(pos.x(), pos.y())
        self.__populate(page.url(), page.execJavaScript(script))
    
    def alternateText(self):
        """
        Public method to get the alternate text.
        
        @return alternate text
        @rtype str
        """
        return self.__alternateText
    
    def boundingRect(self):
        """
        Public method to get the bounding rectangle.
        
        @return bounding rectangle
        @rtype QRect
        """
        return QRect(self.__boundingRect)
    
    def imageUrl(self):
        """
        Public method to get the URL of an image.
        
        @return image URL
        @rtype QUrl
        """
        return self.__imageUrl
    
    def isContentEditable(self):
        """
        Public method to check for editable content.
        
        @return flag indicating editable content
        @rtype bool
        """
        return self.__isContentEditable
    
    def isContentSelected(self):
        """
        Public method to check for selected content.
        
        @return flag indicating selected content
        @rtype bool
        """
        return self.__isContentSelected
    
    def isNull(self):
        """
        Public method to test, if the hit test is empty.
        
        @return flag indicating an empty object
        @rtype bool
        """
        return self.__isNull
    
    def linkTitle(self):
        """
        Public method to get the title for a link element.
        
        @return title for a link element
        @rtype str
        """
        return self.__linkTitle
    
    def linkUrl(self):
        """
        Public method to get the URL for a link element.
        
        @return URL for a link element
        @rtype QUrl
        """
        return self.__linkUrl
    
    def mediaUrl(self):
        """
        Public method to get the URL for a media element.
        
        @return URL for a media element
        @rtype QUrl
        """
        return self.__mediaUrl
    
    def mediaPaused(self):
        """
        Public method to check, if a media element is paused.
        
        @return flag indicating a paused media element
        @rtype bool
        """
        return self.__isMediaPaused
    
    def mediaMuted(self):
        """
        Public method to check, if a media element is muted.
        
        @return flag indicating a muted media element
        @rtype bool
        """
        return self.__isMediaMuted
    
    def pos(self):
        """
        Public method to get the position of the hit test.
        
        @return position of hit test
        @rtype QPoint
        """
        return QPoint(self.__pos)
    
    def tagName(self):
        """
        Public method to get the name of the tested tag.
        
        @return name of the tested tag
        @rtype str
        """
        return self.__tagName
    
    def __populate(self, url, res):
        """
        Private method to populate the object.
        
        @param url URL of the tested page
        @type QUrl
        @param res dictionary with result data from JavaScript
        @type dict
        """
        if not res:
            return
        
        self.__alternateText = res["alternateText"]
        self.__imageUrl = QUrl(res["imageUrl"])
        self.__isContentEditable = res["contentEditable"]
        self.__isContentSelected = res["contentSelected"]
        self.__linkTitle = res["linkTitle"]
        self.__linkUrl = QUrl(res["linkUrl"])
        self.__mediaUrl = QUrl(res["mediaUrl"])
        self.__isMediaPaused = res["mediaPaused"]
        self.__isMediaMuted = res["mediaMuted"]
        self.__tagName = res["tagName"]
        
        rect = res["boundingRect"]
        if len(rect) == 4:
            self.__boundingRect = QRect(int(rect[0]), int(rect[1]),
                                        int(rect[2]), int(rect[3]))
        
        if not self.__imageUrl.isEmpty():
            self.__imageUrl = url.resolved(self.__imageUrl)
        if not self.__linkUrl.isEmpty():
            self.__linkUrl = url.resolved(self.__linkUrl)
        if not self.__mediaUrl.isEmpty():
            self.__mediaUrl = url.resolved(self.__mediaUrl)
