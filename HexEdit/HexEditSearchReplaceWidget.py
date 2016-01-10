# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a search and replace widget for the hex editor.
"""

from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSlot, Qt, QByteArray
from PyQt5.QtWidgets import QWidget

from E5Gui.E5Action import E5Action
from E5Gui import E5MessageBox

import UI.PixmapCache


class HexEditSearchReplaceWidget(QWidget):
    """
    Class implementing a search and replace widget for the hex editor.
    """
    def __init__(self, editor, replace=False, parent=None):
        """
        Constructor
        
        @param editor reference to the hex editor widget
        @type HexEditWidget
        @param replace flag indicating a replace widget
        @type bool
        @param parent reference to the parent widget
        @type QWidget
        """
        super(HexEditSearchReplaceWidget, self).__init__(parent)
        
        self.__replace = replace
        self.__editor = editor
        
        self.__findHistory = []
        if replace:
            from .Ui_HexEditReplaceWidget import Ui_HexEditReplaceWidget
            self.__replaceHistory = []
            self.__ui = Ui_HexEditReplaceWidget()
        else:
            from .Ui_HexEditSearchWidget import Ui_HexEditSearchWidget
            self.__ui = Ui_HexEditSearchWidget()
        self.__ui.setupUi(self)
        
        self.__ui.closeButton.setIcon(UI.PixmapCache.getIcon("close.png"))
        self.__ui.findPrevButton.setIcon(
            UI.PixmapCache.getIcon("1leftarrow.png"))
        self.__ui.findNextButton.setIcon(
            UI.PixmapCache.getIcon("1rightarrow.png"))
        
        if replace:
            self.__ui.replaceButton.setIcon(
                UI.PixmapCache.getIcon("editReplace.png"))
            self.__ui.replaceSearchButton.setIcon(
                UI.PixmapCache.getIcon("editReplaceSearch.png"))
            self.__ui.replaceAllButton.setIcon(
                UI.PixmapCache.getIcon("editReplaceAll.png"))
        
        self.__ui.findtextCombo.setCompleter(None)
        self.__ui.findtextCombo.lineEdit().returnPressed.connect(
            self.__findByReturnPressed)
        if replace:
            self.__ui.replacetextCombo.setCompleter(None)
            self.__ui.replacetextCombo.lineEdit().returnPressed.connect(
                self.on_replaceButton_clicked)
        
        self.findNextAct = E5Action(
            self.tr('Find Next'),
            self.tr('Find Next'),
            0, 0, self, 'hexEditor_search_widget_find_next')
        self.findNextAct.triggered.connect(self.on_findNextButton_clicked)
        self.findNextAct.setEnabled(False)
        self.__ui.findtextCombo.addAction(self.findNextAct)
        
        self.findPrevAct = E5Action(
            self.tr('Find Prev'),
            self.tr('Find Prev'),
            0, 0, self, 'hexEditor_search_widget_find_prev')
        self.findPrevAct.triggered.connect(self.on_findPrevButton_clicked)
        self.findPrevAct.setEnabled(False)
        self.__ui.findtextCombo.addAction(self.findPrevAct)
        
        self.__havefound = False
    
    def on_findtextCombo_editTextChanged(self, txt):
        """
        Private slot to enable/disable the find buttons.
        
        @param txt text of the find text combo (string)
        """
        if not txt:
            self.__ui.findNextButton.setEnabled(False)
            self.findNextAct.setEnabled(False)
            self.__ui.findPrevButton.setEnabled(False)
            self.findPrevAct.setEnabled(False)
            if self.__replace:
                self.__ui.replaceButton.setEnabled(False)
                self.__ui.replaceSearchButton.setEnabled(False)
                self.__ui.replaceAllButton.setEnabled(False)
        else:
            self.__ui.findNextButton.setEnabled(True)
            self.findNextAct.setEnabled(True)
            self.__ui.findPrevButton.setEnabled(True)
            self.findPrevAct.setEnabled(True)
            if self.__replace:
                self.__ui.replaceButton.setEnabled(False)
                self.__ui.replaceSearchButton.setEnabled(False)
                self.__ui.replaceAllButton.setEnabled(True)
    
    def __getContent(self, replace=False):
        """
        Private method to get the contents of the find/replace combo as
        a bytearray.
        
        @param replace flag indicating to retrieve the replace contents
        @type bool
        @return search or replace term as text and binary data
        @rtype tuple of bytearray and str
        """
        if replace:
            textCombo = self.__ui.replacetextCombo
            formatCombo = self.__ui.replaceFormatCombo
            history = self.__replaceHistory
        else:
            textCombo = self.__ui.findtextCombo
            formatCombo = self.__ui.findFormatCombo
            history = self.__findHistory
        
        txt = textCombo.currentText()
        idx = formatCombo.currentIndex()
        if idx == 0:        # hex format
            ba = bytearray(QByteArray.fromHex(
                bytes(txt, encoding="ascii")))
        else:
            ba = bytearray(txt, encoding="utf-8")
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        if txt in history:
            history.remove(txt)
        history.insert(0, txt)
        textCombo.clear()
        textCombo.addItems(history)
        
        return ba, txt
    
    @pyqtSlot()
    def on_findNextButton_clicked(self):
        """
        Private slot to find the next occurrence.
        """
        self.findPrevNext(False)
    
    @pyqtSlot()
    def on_findPrevButton_clicked(self):
        """
        Private slot to find the previous occurrence.
        """
        self.findPrevNext(True)
    
    def findPrevNext(self, prev=False):
        """
        Public slot to find the next occurrence of the search term.
        
        @param prev flag indicating a backwards search
        @type bool
        @return flag indicating a successful search
        @rtype bool
        """
        if not self.__havefound or not self.__ui.findtextCombo.currentText():
            self.show()
            return
        
        self.__findBackwards = prev
        ba, txt = self.__getContent()
        
        idx = -1
        if len(ba) > 0:
            startIndex = self.__editor.cursorPosition() // 2
            if prev:
                if self.__editor.hasSelection() and \
                        startIndex == self.__editor.getSelectionEnd():
                    # skip to the selection start
                    startIndex = self.__editor.getSelectionBegin()
                idx = self.__editor.lastIndexOf(ba, startIndex)
            else:
                if self.__editor.hasSelection() and \
                        startIndex == self.__editor.getSelectionBegin() - 1:
                    # skip to the selection end
                    startIndex = self.__editor.getSelectionEnd()
                idx = self.__editor.indexOf(ba, startIndex)
        
        if idx >= 0:
            if self.__replace:
                self.__ui.replaceButton.setEnabled(True)
                self.__ui.replaceSearchButton.setEnabled(True)
        else:
            E5MessageBox.information(
                self, self.windowTitle(),
                self.tr("'{0}' was not found.").format(txt))
        
        return idx >= 0
    
    def __findByReturnPressed(self):
        """
        Private slot to handle a return pressed in the find combo.
        """
        if self.__findBackwards:
            self.findPrevNext(True)
        else:
            self.findPrevNext(False)

    @pyqtSlot()
    def on_replaceButton_clicked(self):
        """
        Private slot to replace one occurrence of data.
        """
        self.__doReplace(False)
    
    @pyqtSlot()
    def on_replaceSearchButton_clicked(self):
        """
        Private slot to replace one occurrence of data and search for the next
        one.
        """
        self.__doReplace(True)
    
    def __doReplace(self, searchNext):
        """
        Private method to replace one occurrence of data.
        
        @param searchNext flag indicating to search for the next occurrence
        (boolean).
        """
        # Check enabled status due to dual purpose usage of this method
        if not self.__ui.replaceButton.isEnabled() and \
           not self.__ui.replaceSearchButton.isEnabled():
            return
        
        fba, ftxt = self.__getContent(False)
        rba, rtxt = self.__getContent(True)
        
        ok = False
        if self.__editor.hasSelection():
            # we did a successful search before
            startIdx = self.__editor.getSelectionBegin()
            self.__editor.replaceByteArray(startIdx, len(fba), rba)
            
            if searchNext:
                ok = self.findPrevNext(self.__findBackwards)
        
        if not ok:
            self.__ui.replaceButton.setEnabled(False)
            self.__ui.replaceSearchButton.setEnabled(False)
    
    @pyqtSlot()
    def on_replaceAllButton_clicked(self):
        """
        Private slot to replace all occurrences of data.
        """
        replacements = 0
        
        cursorPosition = self.__editor.cursorPosition()
        
        fba, ftxt = self.__getContent(False)
        rba, rtxt = self.__getContent(True)
        
        idx = 0
        while idx >= 0:
            idx = self.__editor.indexOf(fba, idx)
            if idx >= 0:
                self.__editor.replaceByteArray(idx, len(fba), rba)
                idx += len(rba)
                replacements += 1
        
        if replacements:
            E5MessageBox.information(
                self, self.windowTitle(),
                self.tr("Replaced {0} occurrences.")
                .format(replacements))
        else:
            E5MessageBox.information(
                self, self.windowTitle(),
                self.tr("Nothing replaced because '{0}' was not found.")
                .format(ftxt))
        
        self.__editor.setCursorPosition(cursorPosition)
        self.__editor.ensureVisible()
    
    def __showFind(self, text=''):
        """
        Private method to display this widget in find mode.
        
        @param text text to be shown in the findtext edit (string)
        """
        self.__replace = False
        
        self.__ui.findtextCombo.clear()
        self.__ui.findtextCombo.addItems(self.__findHistory)
        self.__ui.findtextCombo.setEditText(text)
        self.__ui.findtextCombo.lineEdit().selectAll()
        self.__ui.findtextCombo.setFocus()
        self.on_findtextCombo_editTextChanged(text)
        
        self.__havefound = True
        self.__findBackwards = False
    
    def __showReplace(self, text=''):
        """
        Private slot to display this widget in replace mode.
        
        @param text text to be shown in the findtext edit
        """
        self.__replace = True
        
        self.__ui.findtextCombo.clear()
        self.__ui.findtextCombo.addItems(self.__findHistory)
        self.__ui.findtextCombo.setEditText(text)
        self.__ui.findtextCombo.lineEdit().selectAll()
        self.__ui.findtextCombo.setFocus()
        self.on_findtextCombo_editTextChanged(text)
        
        self.__ui.replacetextCombo.clear()
        self.__ui.replacetextCombo.addItems(self.__replaceHistory)
        self.__ui.replacetextCombo.setEditText('')
        
        self.__havefound = True
        self.__findBackwards = False
    
    def show(self, text=''):
        """
        Public slot to show the widget.
        
        @param text text to be shown in the findtext edit (string)
        """
        if self.__replace:
            self.__showReplace(text)
        else:
            self.__showFind(text)
        super(HexEditSearchReplaceWidget, self).show()
        self.activateWindow()
    
    @pyqtSlot()
    def on_closeButton_clicked(self):
        """
        Private slot to close the widget.
        """
        self.__editor.setFocus(Qt.OtherFocusReason)
        self.close()

    def keyPressEvent(self, event):
        """
        Protected slot to handle key press events.
        
        @param event reference to the key press event (QKeyEvent)
        """
        if event.key() == Qt.Key_Escape:
            self.close()
