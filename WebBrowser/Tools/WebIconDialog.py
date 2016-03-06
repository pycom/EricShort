# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to manage the Favicons.
"""

from PyQt5.QtCore import pyqtSlot, Qt, QPoint
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QMenu

from .Ui_WebIconDialog import Ui_WebIconDialog


class WebIconDialog(QDialog, Ui_WebIconDialog):
    """
    Class implementing a dialog to manage the Favicons.
    """
    def __init__(self, iconsDB, parent=None):
        """
        Constructor
        
        @param iconsDB icons database
        @type dict
        @param parent reference to the parent widget
        @type QWidget
        """
        super(WebIconDialog, self).__init__(parent)
        self.setupUi(self)
        
        for url, icon in iconsDB.items():
            itm = QTreeWidgetItem(self.iconsList, [url])
            itm.setIcon(0, icon)
        self.iconsList.sortItems(0, Qt.AscendingOrder)
        
        self.__setRemoveButtons()
    
    def __setRemoveButtons(self):
        """
        Private method to set the state of the 'remove' buttons.
        """
        self.removeAllButton.setEnabled(self.iconsList.topLevelItemCount() > 0)
        self.removeButton.setEnabled(len(self.iconsList.selectedItems()) > 0)
    
    @pyqtSlot(QPoint)
    def on_iconsList_customContextMenuRequested(self, pos):
        """
        Private slot to show the context menu.
        
        @param pos cursor position
        @type QPoint
        """
        menu = QMenu()
        menu.addAction(
            self.tr("Remove Selected"),
            self.on_removeButton_clicked).setEnabled(
            len(self.iconsList.selectedItems()) > 0)
        menu.addAction(
            self.tr("Remove All"),
            self.on_removeAllButton_clicked).setEnabled(
            self.iconsList.topLevelItemCount() > 0)
        
        menu.exec_(self.iconsList.mapToGlobal(pos))
    
    @pyqtSlot()
    def on_iconsList_itemSelectionChanged(self):
        """
        Private slot handling the selection of entries.
        """
        self.__setRemoveButtons()
    
    @pyqtSlot()
    def on_removeButton_clicked(self):
        """
        Private slot to remove the selected items.
        """
        for itm in self.iconsList.selectedItems():
            index = self.iconsList.indexOfTopLevelItem(itm)
            self.iconsList.takeTopLevelItem(index)
            del itm
    
    @pyqtSlot()
    def on_removeAllButton_clicked(self):
        """
        Private slot to remove all entries.
        """
        self.iconsList.clear()
    
    def getUrls(self):
        """
        Public method to get the list of URLs.
        
        @return list of URLs
        @rtype list of str
        """
        urls = []
        for index in range(self.iconsList.topLevelItemCount()):
            urls.append(self.iconsList.topLevelItem(index).text(0))
        
        return urls
