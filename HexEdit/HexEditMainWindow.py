# -*- coding: utf-8 -*-

# Copyright (c) 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the hex editor main window.
"""

from __future__ import unicode_literals

import os

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QFile, QFileInfo, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWhatsThis, QLabel

from E5Gui.E5Action import E5Action
from E5Gui.E5MainWindow import E5MainWindow
from E5Gui import E5FileDialog, E5MessageBox

from .HexEditWidget import HexEditWidget

import UI.PixmapCache
import UI.Config

import Preferences


# TODO: implement a configuration page for the hex editor
# TODO: implement an action in the eric IDE to open a hex editor
class HexEditMainWindow(E5MainWindow):
    """
    Class implementing the web browser main window.
    
    @signal editorClosed() emitted after the window was requested to close down
    """
    editorClosed = pyqtSignal()
    
    windows = []
    
    def __init__(self, fileName="", parent=None, fromEric=False, project=None):
        """
        Constructor
        
        @param fileName name of a file to load on startup (string)
        @param parent parent widget of this window (QWidget)
        @keyparam fromEric flag indicating whether it was called from within
            eric6 (boolean)
        @keyparam project reference to the project object (Project)
        """
        super(HexEditMainWindow, self).__init__(parent)
        self.setObjectName("eric6_hex_editor")
        
        self.fromEric = fromEric
        self.setWindowIcon(UI.PixmapCache.getIcon("hexEditor.png"))
        
        if not self.fromEric:
            self.setStyle(Preferences.getUI("Style"),
                          Preferences.getUI("StyleSheet"))
        
        self.__editor = HexEditWidget()
        self.setCentralWidget(self.__editor)
        
        g = Preferences.getGeometry("HexEditorGeometry")
        if g.isEmpty():
            s = QSize(600, 500)
            self.resize(s)
        else:
            self.restoreGeometry(g)
        
        self.__initActions()
        self.__initMenus()
        self.__initToolbars()
        self.__createStatusBar()
        
        self.__class__.windows.append(self)
        
        self.__editor.currentAddressChanged.connect(self.__showAddress)
        self.__editor.currentSizeChanged.connect(self.__showSize)
        self.__editor.dataChanged.connect(self.__modificationChanged)
        self.__editor.overwriteModeChanged.connect(self.__showEditMode)
        self.__editor.readOnlyChanged.connect(self.__showReadOnlyMode)
        
        self.__project = project
        self.__lastOpenPath = ""
        self.__lastSavePath = ""
        
        self.__setCurrentFile("")
        if fileName:
            self.__loadHexFile(fileName)
        
        self.__checkActions()
    
    def __initActions(self):
        """
        Private method to define the user interface actions.
        """
        # list of all actions
        self.__actions = []
        
        self.__initFileActions()
        self.__initEditActions()
##        self.__initViewActions()
##        self.__initToolsActions()
        self.__initHelpActions()
        
    def __initFileActions(self):
        """
        Private method to define the file related user interface actions.
        """
        self.newWindowAct = E5Action(
            self.tr('New Window'),
            UI.PixmapCache.getIcon("newWindow.png"),
            self.tr('New &Window'),
            0, 0, self, 'hexEditor_file_new_window')
        self.newWindowAct.setStatusTip(self.tr(
            'Open a binary file for editing in a new hex editor window'))
        self.newWindowAct.setWhatsThis(self.tr(
            """<b>New Window</b>"""
            """<p>This opens a binary file for editing in a new hex editor"""
            """ window.</p>"""
        ))
        self.newWindowAct.triggered.connect(self.__openHexFileNewWindow)
        self.__actions.append(self.newWindowAct)
        
        self.openAct = E5Action(
            self.tr('Open'),
            UI.PixmapCache.getIcon("open.png"),
            self.tr('&Open...'),
            QKeySequence(self.tr("Ctrl+O", "File|Open")),
            0, self, 'hexEditor_file_open')
        self.openAct.setStatusTip(self.tr('Open a binary file for editing'))
        self.openAct.setWhatsThis(self.tr(
            """<b>Open File</b>"""
            """<p>This opens a binary file for editing."""
            """ It pops up a file selection dialog.</p>"""
        ))
        self.openAct.triggered.connect(self.__openHexFile)
        self.__actions.append(self.openAct)
        
        self.openReadOnlyAct = E5Action(
            self.tr('Open Read Only'),
            self.tr('Open Read Only...'),
            0, 0, self, 'hexEditor_file_open_read_only')
        self.openReadOnlyAct.setStatusTip(self.tr(
            'Open a binary file for viewing'))
        self.openReadOnlyAct.setWhatsThis(self.tr(
            """<b>Open Read Only</b>"""
            """<p>This opens a binary file for viewing (i.e. in read only"""
            """ mode). It pops up a file selection dialog.</p>"""
        ))
        self.openReadOnlyAct.triggered.connect(self.__openHexFileReadOnly)
        self.__actions.append(self.openReadOnlyAct)
        
        self.saveAct = E5Action(
            self.tr('Save'),
            UI.PixmapCache.getIcon("fileSave.png"),
            self.tr('&Save'),
            QKeySequence(self.tr("Ctrl+S", "File|Save")),
            0, self, 'hexEditor_file_save')
        self.saveAct.setStatusTip(self.tr('Save the current binary file'))
        self.saveAct.setWhatsThis(self.tr(
            """<b>Save File</b>"""
            """<p>Save the contents of the hex editor window.</p>"""
        ))
        self.saveAct.triggered.connect(self.__saveHexFile)
        self.__actions.append(self.saveAct)
        
        self.saveAsAct = E5Action(
            self.tr('Save As'),
            UI.PixmapCache.getIcon("fileSaveAs.png"),
            self.tr('Save &As...'),
            QKeySequence(self.tr("Shift+Ctrl+S", "File|Save As")),
            0, self, 'hexEditor_file_save_as')
        self.saveAsAct.setStatusTip(
            self.tr('Save the current binary data to a new file'))
        self.saveAsAct.setWhatsThis(self.tr(
            """<b>Save As...</b>"""
            """<p>Saves the current binary data to a new file.</p>"""
        ))
        self.saveAsAct.triggered.connect(self.__saveHexFileAs)
        self.__actions.append(self.saveAsAct)
        
        self.saveReadableAct = E5Action(
            self.tr('Save As Readable'),
            self.tr('Save As &Readable...'),
            0, 0, self, 'hexEditor_file_save_readable')
        self.saveReadableAct.setStatusTip(
            self.tr('Save the current binary data to a new file in a readable'
                    ' format'))
        self.saveReadableAct.setWhatsThis(self.tr(
            """<b>Save As Readable...</b>"""
            """<p>Saves the current binary data to a new file in a readable"""
            """ format.</p>"""
        ))
        self.saveReadableAct.triggered.connect(self.__saveHexFileReadable)
        self.__actions.append(self.saveReadableAct)
        
        self.closeAct = E5Action(
            self.tr('Close'),
            UI.PixmapCache.getIcon("close.png"),
            self.tr('&Close'),
            QKeySequence(self.tr("Ctrl+W", "File|Close")),
            0, self, 'hexEditor_file_close')
        self.closeAct.setStatusTip(self.tr(
            'Close the current hex editor window'))
        self.closeAct.setWhatsThis(self.tr(
            """<b>Close</b>"""
            """<p>Closes the current hex editor window.</p>"""
        ))
        self.closeAct.triggered.connect(self.close)
        self.__actions.append(self.closeAct)
        
        self.closeAllAct = E5Action(
            self.tr('Close All'),
            self.tr('Close &All'),
            0, 0, self, 'hexEditor_file_close_all')
        self.closeAllAct.setStatusTip(self.tr(
            'Close all hex editor windows'))
        self.closeAllAct.setWhatsThis(self.tr(
            """<b>Close All</b>"""
            """<p>Closes all hex editor windows.</p>"""
        ))
        self.closeAllAct.triggered.connect(self.__closeAll)
        self.__actions.append(self.closeAllAct)
        
        self.closeOthersAct = E5Action(
            self.tr('Close Others'),
            self.tr('Close Others'),
            0, 0, self, 'hexEditor_file_close_others')
        self.closeOthersAct.setStatusTip(self.tr(
            'Close all hex other editor windows'))
        self.closeOthersAct.setWhatsThis(self.tr(
            """<b>Close Others</b>"""
            """<p>Closes all other hex editor windows.</p>"""
        ))
        self.closeOthersAct.triggered.connect(self.__closeOthers)
        self.__actions.append(self.closeOthersAct)
        
        self.exitAct = E5Action(
            self.tr('Quit'),
            UI.PixmapCache.getIcon("exit.png"),
            self.tr('&Quit'),
            QKeySequence(self.tr("Ctrl+Q", "File|Quit")),
            0, self, 'hexEditor_file_quit')
        self.exitAct.setStatusTip(self.tr('Quit the hex editor'))
        self.exitAct.setWhatsThis(self.tr(
            """<b>Quit</b>"""
            """<p>Quit the hex editor.</p>"""
        ))
        if not self.fromEric:
            self.exitAct.triggered.connect(self.__closeAll)
        self.__actions.append(self.exitAct)
    
    def __initEditActions(self):
        """
        Private method to create the Edit actions.
        """
        self.undoAct = E5Action(
            self.tr('Undo'),
            UI.PixmapCache.getIcon("editUndo.png"),
            self.tr('&Undo'),
            QKeySequence(self.tr("Ctrl+Z", "Edit|Undo")),
            QKeySequence(self.tr("Alt+Backspace", "Edit|Undo")),
            self, 'hexEditor_edit_undo')
        self.undoAct.setStatusTip(self.tr('Undo the last change'))
        self.undoAct.setWhatsThis(self.tr(
            """<b>Undo</b>"""
            """<p>Undo the last change done.</p>"""
        ))
        self.undoAct.triggered.connect(self.__editor.undo)
        self.__actions.append(self.undoAct)
        
        self.redoAct = E5Action(
            self.tr('Redo'),
            UI.PixmapCache.getIcon("editRedo.png"),
            self.tr('&Redo'),
            QKeySequence(self.tr("Ctrl+Shift+Z", "Edit|Redo")),
            0, self, 'hexEditor_edit_redo')
        self.redoAct.setStatusTip(self.tr('Redo the last change'))
        self.redoAct.setWhatsThis(self.tr(
            """<b>Redo</b>"""
            """<p>Redo the last change done.</p>"""
        ))
        self.redoAct.triggered.connect(self.__editor.redo)
        self.__actions.append(self.redoAct)
        
        self.revertAct = E5Action(
            self.tr('Revert to last saved state'),
            self.tr('Re&vert to last saved state'),
            QKeySequence(self.tr("Ctrl+Y", "Edit|Revert")),
            0,
            self, 'hexEditor_edit_revert')
        self.revertAct.setStatusTip(self.tr('Revert to last saved state'))
        self.revertAct.setWhatsThis(self.tr(
            """<b>Revert to last saved state</b>"""
            """<p>Undo all changes up to the last saved state of the"""
            """ editor.</p>"""
        ))
        self.revertAct.triggered.connect(self.__editor.revertToUnmodified)
        self.__actions.append(self.revertAct)
        
        self.cutAct = E5Action(
            self.tr('Cut'),
            UI.PixmapCache.getIcon("editCut.png"),
            self.tr('Cu&t'),
            QKeySequence(self.tr("Ctrl+X", "Edit|Cut")),
            QKeySequence(self.tr("Shift+Del", "Edit|Cut")),
            self, 'hexEditor_edit_cut')
        self.cutAct.setStatusTip(self.tr('Cut the selection'))
        self.cutAct.setWhatsThis(self.tr(
            """<b>Cut</b>"""
            """<p>Cut the selected binary area to the clipboard.</p>"""
        ))
        self.cutAct.triggered.connect(self.__editor.cut)
        self.__actions.append(self.cutAct)
        
        self.copyAct = E5Action(
            self.tr('Copy'),
            UI.PixmapCache.getIcon("editCopy.png"),
            self.tr('&Copy'),
            QKeySequence(self.tr("Ctrl+C", "Edit|Copy")),
            QKeySequence(self.tr("Ctrl+Ins", "Edit|Copy")),
            self, 'hexEditor_edit_copy')
        self.copyAct.setStatusTip(self.tr('Copy the selection'))
        self.copyAct.setWhatsThis(self.tr(
            """<b>Copy</b>"""
            """<p>Copy the selected binary area to the clipboard.</p>"""
        ))
        self.copyAct.triggered.connect(self.__editor.copy)
        self.__actions.append(self.copyAct)
        
        self.pasteAct = E5Action(
            self.tr('Paste'),
            UI.PixmapCache.getIcon("editPaste.png"),
            self.tr('&Paste'),
            QKeySequence(self.tr("Ctrl+V", "Edit|Paste")),
            QKeySequence(self.tr("Shift+Ins", "Edit|Paste")),
            self, 'hexEditor_edit_paste')
        self.pasteAct.setStatusTip(self.tr('Paste the clipboard contents'))
        self.pasteAct.setWhatsThis(self.tr(
            """<b>Paste</b>"""
            """<p>Paste the clipboard contents.</p>"""
        ))
        self.pasteAct.triggered.connect(self.__editor.paste)
        self.__actions.append(self.pasteAct)
        
        self.selectAllAct = E5Action(
            self.tr('Select All'),
            UI.PixmapCache.getIcon("editSelectAll.png"),
            self.tr('&Select All'),
            QKeySequence(self.tr("Ctrl+A", "Edit|Select All")),
            0,
            self, 'hexEditor_edit_select_all')
        self.selectAllAct.setStatusTip(self.tr(
            'Select the complete binary data'))
        self.selectAllAct.setWhatsThis(self.tr(
            """<b>Select All</b>"""
            """<p>Selects the complete binary data.</p>"""
        ))
        self.selectAllAct.triggered.connect(self.__editor.selectAll)
        self.__actions.append(self.selectAllAct)
        
        self.deselectAllAct = E5Action(
            self.tr('Deselect all'),
            self.tr('&Deselect all'),
            QKeySequence(self.tr("Alt+Ctrl+A", "Edit|Deselect all")),
            0,
            self, 'hexEditor_edit_deselect_all')
        self.deselectAllAct.setStatusTip(self.tr('Deselect all binary data'))
        self.deselectAllAct.setWhatsThis(self.tr(
            """<b>Deselect All</b>"""
            """<p>Deselect all all binary data.</p>"""
        ))
        self.deselectAllAct.triggered.connect(self.__editor.deselectAll)
        self.__actions.append(self.deselectAllAct)
        
        self.saveSelectionReadableAct = E5Action(
            self.tr('Save Selection Readable'),
            self.tr('Save Selection Readable...'),
            0, 0, self, 'hexEditor_edit_selection_save_readable')
        self.saveSelectionReadableAct.setStatusTip(
            self.tr('Save the binary data of the current selection to a file'
                    ' in a readable format'))
        self.saveSelectionReadableAct.setWhatsThis(self.tr(
            """<b>Save Selection Readable...</b>"""
            """<p>Saves the binary data of the current selection to a file"""
            """ in a readable format.</p>"""
        ))
        self.saveSelectionReadableAct.triggered.connect(
            self.__saveSelectionReadable)
        self.__actions.append(self.saveSelectionReadableAct)
        
        self.readonlyAct = E5Action(
            self.tr('Set Read Only'),
            self.tr('Set Read Only'),
            0, 0, self, 'hexEditor_edit_readonly', True)
        self.readonlyAct.setStatusTip(self.tr(
            'Change the edit mode to read only'))
        self.readonlyAct.setWhatsThis(self.tr(
            """<b>Set Read Only</b>"""
            """<p>This changes the edit mode to read only (i.e. to view"""
            """ mode).</p>"""
        ))
        self.readonlyAct.setChecked(False)
        self.readonlyAct.toggled[bool].connect(self.__editor.setReadOnly)
        self.__actions.append(self.readonlyAct)
        
        self.redoAct.setEnabled(False)
        self.__editor.canRedoChanged.connect(self.redoAct.setEnabled)
        
        self.undoAct.setEnabled(False)
        self.__editor.canUndoChanged.connect(self.undoAct.setEnabled)
        
        self.revertAct.setEnabled(False)
        self.__editor.dataChanged.connect(self.revertAct.setEnabled)
        
        self.cutAct.setEnabled(False)
        self.copyAct.setEnabled(False)
        self.saveSelectionReadableAct.setEnabled(False)
        self.__editor.selectionAvailable.connect(self.__checkActions)
        self.__editor.selectionAvailable.connect(self.copyAct.setEnabled)
        self.__editor.selectionAvailable.connect(
            self.saveSelectionReadableAct.setEnabled)
    
    def __initHelpActions(self):
        """
        Private method to create the Help actions.
        """
        self.aboutAct = E5Action(
            self.tr('About'),
            self.tr('&About'),
            0, 0, self, 'hexEditor_help_about')
        self.aboutAct.setStatusTip(self.tr(
            'Display information about this software'))
        self.aboutAct.setWhatsThis(self.tr(
            """<b>About</b>"""
            """<p>Display some information about this software.</p>"""))
        self.aboutAct.triggered.connect(self.__about)
        self.__actions.append(self.aboutAct)
        
        self.aboutQtAct = E5Action(
            self.tr('About Qt'),
            self.tr('About &Qt'),
            0, 0, self, 'hexEditor_help_about_qt')
        self.aboutQtAct.setStatusTip(
            self.tr('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.tr(
            """<b>About Qt</b>"""
            """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.aboutQtAct.triggered.connect(self.__aboutQt)
        self.__actions.append(self.aboutQtAct)
        
        self.whatsThisAct = E5Action(
            self.tr('What\'s This?'),
            UI.PixmapCache.getIcon("whatsThis.png"),
            self.tr('&What\'s This?'),
            QKeySequence(self.tr("Shift+F1", "Help|What's This?'")),
            0, self, 'hexEditor_help_whats_this')
        self.whatsThisAct.setStatusTip(self.tr('Context sensitive help'))
        self.whatsThisAct.setWhatsThis(self.tr(
            """<b>Display context sensitive help</b>"""
            """<p>In What's This? mode, the mouse cursor shows an arrow"""
            """ with a question mark, and you can click on the interface"""
            """ elements to get a short description of what they do and"""
            """ how to use them. In dialogs, this feature can be accessed"""
            """ using the context help button in the titlebar.</p>"""
        ))
        self.whatsThisAct.triggered.connect(self.__whatsThis)
        self.__actions.append(self.whatsThisAct)
    
    def __initMenus(self):
        """
        Private method to create the menus.
        """
        mb = self.menuBar()
        
        menu = mb.addMenu(self.tr('&File'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.newWindowAct)
        menu.addAction(self.openAct)
        menu.addAction(self.openReadOnlyAct)
        menu.addSeparator()
        menu.addAction(self.saveAct)
        menu.addAction(self.saveAsAct)
        menu.addAction(self.saveReadableAct)
        menu.addSeparator()
        menu.addAction(self.closeAct)
        menu.addAction(self.closeOthersAct)
        if self.fromEric:
            menu.addAction(self.closeAllAct)
        else:
            menu.addSeparator()
            menu.addAction(self.exitAct)
        
        menu = mb.addMenu(self.tr("&Edit"))
        menu.setTearOffEnabled(True)
        menu.addAction(self.undoAct)
        menu.addAction(self.redoAct)
        menu.addAction(self.revertAct)
        menu.addSeparator()
        menu.addAction(self.cutAct)
        menu.addAction(self.copyAct)
        menu.addAction(self.pasteAct)
        menu.addSeparator()
        menu.addAction(self.selectAllAct)
        menu.addAction(self.deselectAllAct)
        menu.addAction(self.saveSelectionReadableAct)
        menu.addSeparator()
        menu.addAction(self.readonlyAct)
        
        mb.addSeparator()
        
        menu = mb.addMenu(self.tr("&Help"))
        menu.addAction(self.aboutAct)
        menu.addAction(self.aboutQtAct)
        menu.addSeparator()
        menu.addAction(self.whatsThisAct)
    
    def __initToolbars(self):
        """
        Private method to create the toolbars.
        """
        filetb = self.addToolBar(self.tr("File"))
        filetb.setObjectName("FileToolBar")
        filetb.setIconSize(UI.Config.ToolBarIconSize)
        filetb.addAction(self.newWindowAct)
        filetb.addAction(self.openAct)
        filetb.addSeparator()
        filetb.addAction(self.saveAct)
        filetb.addAction(self.saveAsAct)
        filetb.addSeparator()
        filetb.addAction(self.closeAct)
        if not self.fromEric:
            filetb.addAction(self.exitAct)
        
        edittb = self.addToolBar(self.tr("Edit"))
        edittb.setObjectName("EditToolBar")
        edittb.setIconSize(UI.Config.ToolBarIconSize)
        edittb.addAction(self.undoAct)
        edittb.addAction(self.redoAct)
        edittb.addSeparator()
        edittb.addAction(self.cutAct)
        edittb.addAction(self.copyAct)
        edittb.addAction(self.pasteAct)
        
        helptb = self.addToolBar(self.tr("Help"))
        helptb.setObjectName("HelpToolBar")
        helptb.setIconSize(UI.Config.ToolBarIconSize)
        helptb.addAction(self.whatsThisAct)
    
    def __createStatusBar(self):
        """
        Private method to initialize the status bar.
        """
        self.__statusBar = self.statusBar()
        self.__statusBar.setSizeGripEnabled(True)
        
        self.__sbEditMode = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbEditMode)
        self.__sbEditMode.setWhatsThis(self.tr(
            """<p>This part of the status bar displays the edit mode.</p>"""
        ))
        
        self.__sbReadOnly = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbReadOnly)
        self.__sbReadOnly.setWhatsThis(self.tr(
            """<p>This part of the status bar displays the read"""
            """ only mode.</p>"""
        ))

        self.__sbAddress = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbAddress)
        self.__sbAddress.setWhatsThis(self.tr(
            """<p>This part of the status bar displays the cursor"""
            """ address.</p>"""
        ))
        
        self.__showEditMode(self.__editor.overwriteMode())
        self.__showReadOnlyMode(self.__editor.isReadOnly())
        
        self.__sbSize = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbSize)
        self.__sbSize.setWhatsThis(self.tr(
            """<p>This part of the status bar displays the size of the"""
            """ binary data.</p>"""
        ))
    
    @pyqtSlot(int)
    def __showAddress(self, address):
        """
        Private slot to show the address of the cursor position.
        
        @param address address of the cursor
        @type int
        """
        self.__sbAddress.setText(self.tr("Address: {0:#x}").format(address))
    
    @pyqtSlot(bool)
    def __showReadOnlyMode(self, on):
        """
        Private slot to show the read only mode.
        
        @param on flag indicating the read only state
        @type bool
        """
        self.__sbReadOnly.setText(self.tr("ro") if on else self.tr("rw"))
    
    @pyqtSlot(bool)
    def __showEditMode(self, overwrite):
        """
        Private slot to show the edit mode.
        
        @param overwrite flag indicating overwrite mode
        @type bool
        """
        self.__sbEditMode.setText(
            self.tr("Overwrite") if overwrite else self.tr("Insert"))
    
    @pyqtSlot(int)
    def __showSize(self, size):
        """
        Private slot to show the binary data size.
        
        @param size size of the binary data
        @type int
        """
        self.__sbSize.setText(self.tr("Size: {0:n}").format(size))
    
    def closeEvent(self, evt):
        """
        Protected event handler for the close event.
        
        @param evt reference to the close event
            <br />This event is simply accepted after the history has been
            saved and all window references have been deleted.
        @type QCloseEvent
        """
        if self.__maybeSave():
            Preferences.setGeometry("HexEditorGeometry", self.saveGeometry())
            
            try:
                if self.fromEric or len(self.__class__.windows) > 1:
                    del self.__class__.windows[
                        self.__class__.windows.index(self)]
            except ValueError:
                pass
            
            if not self.fromEric:
                Preferences.syncPreferences()
            
            evt.accept()
            self.editorClosed.emit()
        else:
            evt.ignore()
    
    def __openHexFileNewWindow(self):
        """
        Private slot called to open a binary file in new hex editor window.
        """
        if not self.__lastOpenPath:
            if self.__project and self.__project.isOpen():
                self.__lastOpenPath = self.__project.getProjectPath()
        
        fileName = E5FileDialog.getOpenFileName(
            self,
            self.tr("Open binary file in new window"),
            self.__lastOpenPath,
            self.tr("All Files (*)"))
        if fileName:
            he = HexEditMainWindow(fileName=fileName,
                                   parent=self.parent(),
                                   fromEric=self.fromEric,
                                   project=self.__project)
            he.setRecentPaths("", self.__lastSavePath)
            he.show()
    
    def __maybeSave(self):
        """
        Private method to ask the user to save the file, if it was modified.
        
        @return flag indicating, if it is ok to continue
        @rtype bool
        """
        if self.__editor.isModified():
            ret = E5MessageBox.okToClearData(
                self,
                self.tr("eric6 Hex Editor"),
                self.tr("""The loaded file has unsaved changes."""),
                self.__saveHexFile)
            if not ret:
                return False
        return True
    
    def __loadHexFile(self, fileName):
        """
        Private method to load a binary file.
        
        @param fileName name of the binary file to load
        @type str
        """
        file = QFile(fileName)
        if not file.exists():
            E5MessageBox.warning(
                self, self.tr("eric6 Hex Editor"),
                self.tr("The file '{0}' does not exist.")
                .format(fileName))
            return
        
        if not file.open(QFile.ReadOnly):
            E5MessageBox.warning(
                self, self.tr("eric6 Hex Editor"),
                self.tr("Cannot read file '{0}:\n{1}.")
                .format(fileName, file.errorString()))
            return
        
        data = file.readAll()
        file.close()
        
        self.__lastOpenPath = os.path.dirname(fileName)
        self.__editor.setData(data)
        self.__setCurrentFile(fileName)
    
    def __openHexFile(self):
        """
        Private slot to open a binary file.
        """
        if self.__maybeSave():
            if not self.__lastOpenPath:
                if self.__project and self.__project.isOpen():
                    self.__lastOpenPath = self.__project.getProjectPath()
            
            fileName = E5FileDialog.getOpenFileName(
                self,
                self.tr("Open binary file"),
                self.__lastOpenPath,
                self.tr("All Files (*)"))
            if fileName:
                self.__loadHexFile(fileName)
        self.__checkActions()
    
    def __openHexFileReadOnly(self):
        """
        Private slot to open a binary file in read only mode.
        """
        self.__openHexFile()
        self.__editor.setReadOnly(True)
        self.__checkActions()
    
    def __saveHexFile(self):
        """
        Private method to save a binary file.
        
        @return flag indicating success
        @rtype bool
        """
        if not self.__fileName:
            ok = self.__saveHexFileAs()
        else:
            ok = self.__saveHexDataFile(self.__fileName)
        
        if ok:
            self.__editor.undoStack().setClean()
        
        return ok
    
    def __saveHexFileAs(self):
        """
        Private method to save the data to a new file.
        
        @return flag indicating success
        @rtype bool
        """
        if not self.__lastSavePath:
            if self.__project and self.__project.isOpen():
                self.__lastSavePath = self.__project.getProjectPath()
        if not self.__lastSavePath and self.__lastOpenPath:
            self.__lastSavePath = self.__lastOpenPath
        
        fileName = E5FileDialog.getSaveFileName(
            self,
            self.tr("Save binary file"),
            self.__lastSavePath,
            self.tr("All Files (*)"),
            E5FileDialog.Options(E5FileDialog.DontConfirmOverwrite))
        if not fileName:
            return False
        
        if QFileInfo(fileName).exists():
            res = E5MessageBox.yesNo(
                self,
                self.tr("Save binary file"),
                self.tr("<p>The file <b>{0}</b> already exists."
                        " Overwrite it?</p>").format(fileName),
                icon=E5MessageBox.Warning)
            if not res:
                return False
        
        self.__lastSavePath = os.path.dirname(fileName)
        
        return self.__saveHexDataFile(fileName)
    
    def __saveHexDataFile(self, fileName):
        """
        Private method to save the binary data to a file.
        
        @param fileName name of the file to write to
        @type str
        @return flag indicating success
        @rtype bool
        """
        file = QFile(fileName)
        if not file.open(QFile.WriteOnly):
            E5MessageBox.warning(
                self, self.tr("eric6 Hex Editor"),
                self.tr("Cannot write file '{0}:\n{1}.")
                .format(fileName, file.errorString()))
        
            self.__checkActions()
            
            return False
        
        res = file.write(self.__editor.data()) != -1
        file.close()
        
        if not res:
            E5MessageBox.warning(
                self, self.tr("eric6 Hex Editor"),
                self.tr("Cannot write file '{0}:\n{1}.")
                .format(fileName, file.errorString()))
        
            self.__checkActions()
            
            return False
        
        self.__editor.setModified(False, setCleanState=True)
        
        self.__setCurrentFile(fileName)
        self.__statusBar.showMessage(self.tr("File saved"), 2000)
        
        self.__checkActions()
        
        return True
    
    def __saveHexFileReadable(self, selectionOnly=False):
        """
        Private method to save the binary data in readable format.
        
        @param selectionOnly flag indicating to save the selection only
        @type bool
        """
        savePath = self.__lastSavePath
        if not savePath:
            if self.__project and self.__project.isOpen():
                savePath = self.__project.getProjectPath()
        if not savePath and self.__lastOpenPath:
            savePath = self.__lastOpenPath
        
        fileName, selectedFilter = E5FileDialog.getSaveFileNameAndFilter(
            self,
            self.tr("Save to readable file"),
            savePath,
            self.tr("Text Files (*.txt);;All Files (*)"),
            self.tr("Text Files (*.txt)"),
            E5FileDialog.Options(E5FileDialog.DontConfirmOverwrite))
        if not fileName:
            return
        
        ext = QFileInfo(fileName).suffix()
        if not ext:
            ex = selectedFilter.split("(*")[1].split(")")[0]
            if ex:
                fileName += ex
        if QFileInfo(fileName).exists():
            res = E5MessageBox.yesNo(
                self,
                self.tr("Save to readable file"),
                self.tr("<p>The file <b>{0}</b> already exists."
                        " Overwrite it?</p>").format(fileName),
                icon=E5MessageBox.Warning)
            if not res:
                return
        
        file = QFile(fileName)
        if not file.open(QFile.WriteOnly):
            E5MessageBox.warning(
                self, self.tr("eric6 Hex Editor"),
                self.tr("Cannot write file '{0}:\n{1}.")
                .format(fileName, file.errorString()))
            return
        
        if selectionOnly:
            readableData = self.__editor.selectionToReadableString()
        else:
            readableData = self.__editor.toReadableString()
        res = file.write(readableData.encode("latin1")) != -1
        file.close()
        
        if not res:
            E5MessageBox.warning(
                self, self.tr("eric6 Hex Editor"),
                self.tr("Cannot write file '{0}:\n{1}.")
                .format(fileName, file.errorString()))
            return
        
        self.__statusBar.showMessage(self.tr("File saved"), 2000)
    
    def __saveSelectionReadable(self):
        """
        Private method to save the data of the current selection in readable
        format.
        """
        self.__saveHexFileReadable(selectionOnly=True)
    
    def __closeAll(self):
        """
        Private slot to close all windows.
        """
        self.__closeOthers()
        self.close()
    
    def __closeOthers(self):
        """
        Private slot to close all other windows.
        """
        for win in self.__class__.windows[:]:
            if win != self:
                win.close()

    def __setCurrentFile(self, fileName):
        """
        Private method to register the file name of the current file.
        
        @param fileName name of the file to register
        @type str
        """
        self.__fileName = fileName
        
        if not self.__fileName:
            shownName = self.tr("Untitled")
        else:
            shownName = self.__strippedName(self.__fileName)
        
        self.setWindowTitle(self.tr("{0}[*] - {1}")
                            .format(shownName, self.tr("Hex Editor")))
        
        self.setWindowModified(self.__editor.isModified())
    
    def __strippedName(self, fullFileName):
        """
        Private method to return the filename part of the given path.
        
        @param fullFileName full pathname of the given file
        @type str
        @return filename part
        @rtype str
        """
        return QFileInfo(fullFileName).fileName()
    
    def setRecentPaths(self, openPath, savePath):
        """
        Public method to set the last open and save paths.
        
        @param openPath least recently used open path
        @type str
        @param savePath least recently used save path
        @type str
        """
        if openPath:
            self.__lastOpenPath = openPath
        if savePath:
            self.__lastSavePath = savePath
    
    @pyqtSlot()
    def __checkActions(self):
        """
        Private slot to check some actions for their enable/disable status.
        """
        self.saveAct.setEnabled(self.__editor.isModified())
        
        self.cutAct.setEnabled(not self.__editor.isReadOnly() and
                               self.__editor.hasSelection())
        self.pasteAct.setEnabled(not self.__editor.isReadOnly())
    
    @pyqtSlot(bool)
    def __modificationChanged(self, m):
        """
        Private slot to handle the dataChanged signal.
        
        @param m modification status
        @type bool
        """
        self.setWindowModified(m)
        self.__checkActions()
    
    def __about(self):
        """
        Private slot to show a little About message.
        """
        E5MessageBox.about(
            self, self.tr("About eric6 Hex Editor"),
            self.tr("The eric6 Hex Editor is a simple editor component"
                    " to edit binary files."))
    
    def __aboutQt(self):
        """
        Private slot to handle the About Qt dialog.
        """
        E5MessageBox.aboutQt(self, "eric6 Hex Editor")
    
    def __whatsThis(self):
        """
        Private slot called in to enter Whats This mode.
        """
        QWhatsThis.enterWhatsThisMode()
