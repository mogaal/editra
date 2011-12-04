###############################################################################
# Name: _dirtree.py                                                           #
# Purpose: Directory Tree                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library: FileTree

Base class control for displaying a file system in a hierarchical manor.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: _filetree.py 68686 2011-08-13 19:07:25Z CJP $"
__revision__ = "$Revision: 68686 $"

__all__ = ['FileTree',]

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

#-----------------------------------------------------------------------------#

class FileTree(wx.TreeCtrl):
    """Simple base control for displaying directories and files in a
    hierarchical view.

    """
    def __init__(self, parent):
        super(FileTree, self).__init__(parent,
                                       style=wx.TR_HIDE_ROOT|
                                             wx.TR_FULL_ROW_HIGHLIGHT|
                                             wx.TR_LINES_AT_ROOT|
                                             wx.TR_HAS_BUTTONS|
                                             wx.TR_MULTIPLE)

        # Attributes
        self._watch = list() # Root directories to watch
        self._il = wx.ImageList(16, 16)
        
        # Setup
        bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_MENU, (16,16))
        self._il.Add(bmp)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_MENU, (16,16))
        self._il.Add(bmp)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MENU, (16,16))
        self._il.Add(bmp)
        self.SetImageList(self._il)
        self.AddRoot('root')
        self.SetPyData(self.RootItem, "root")

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self._OnGetToolTip)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self._OnItemCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._OnItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self._OnMenu)

    def _OnGetToolTip(self, evt):
        item = evt.GetItem()
        tt = self.DoGetToolTip(item)
        if tt:
            evt.ToolTip = tt
        evt.Skip()

    def _OnItemActivated(self, evt):
        item = evt.GetItem()
        self.DoItemActivated(item)

    def _OnItemCollapsed(self, evt):
        item = evt.GetItem()
        self.DoItemCollapsed(item)

    def _OnItemExpanding(self, evt):
        item = evt.GetItem()
        self.DoItemExpanding(item)

    def _OnMenu(self, evt):
        item = evt.GetItem()
        self.DoShowMenu(item)

    #---- Overridable methods ----#

    def DoGetToolTip(self, item):
        """Get the tooltip to show for an item
        @return: string or None

        """
        data = self.GetItemPyData(item)
        return data

    def DoItemActivated(self, item):
        """Override to handle item activation
        @param item: TreeItem

        """
        pass

    def DoItemCollapsed(self, item):
        """Handle when an item is collapsed
        @param item: TreeItem

        """
        self.DeleteChildren(item)

    def DoItemExpanding(self, item):
        """Handle when an item is expanding
        @param item: TreeItem

        """
        d = self.GetPyData(item)
        if d and os.path.exists(d):
            contents = FileTree.GetDirContents(d)
            for p in contents:
                self.AppendFileNode(item, p)

    def DoShowMenu(self, item):
        """Context menu has been requested for the given item.
        @parm item: TreeItem

        """
        pass

    def GetFileImage(self, path):
        """Get the index of the image from the image list to use
        for the file.
        @param path: Absolute path of file
        @return: long

        """
        # TODO: image handling
        if not os.access(path, os.R_OK):
            img = 2
        else:
            if os.path.isdir(path):
                img = 0 # Directory image
            else:
                img = 1 # Normal file image
        return img

    #---- End Overrides ----#

    #---- Properties ----#

    WatchDirs = property(lambda self: self._watch)

    #---- FileTree Api ---#

    def AddWatchDirectory(self, dname):
        """Add a directory to the controls top level view
        @param dname: directory path

        """
        assert os.path.exists(dname)
        if dname not in self._watch:
            self._watch.append(dname)
            self.AppendFileNode(self.RootItem, dname)

    def RemoveWatchDirectory(self, dname):
        """Remove a directory from the watch list
        @param dname: directory path

        """
        assert os.path.exists(dname)
        if dname in self._watch:
            self._watch.remove(dname)
            nodes = self.GetChildNodes(self.RootItem)
            for node in nodes:
                data = self.GetPyData(node)
                if dname == data:
                    self.Delete(node)
                    break

    def AppendFileNode(self, item, path):
        """Append a child node to the tree
        @param item: TreeItem parent node
        @param path: path to add to node
        @return: new node

        """
        img = self.GetFileImage(path)
        name = os.path.basename(path)
        child = self.AppendItem(item, name, img)
        self.SetPyData(child, path)
        if os.path.isdir(path):
            self.SetItemHasChildren(child, True)
        return child

    def GetChildNodes(self, parent):
        """Get all the TreeItemIds under the given parent
        @param parent: TreeItem
        @return: list of TreeItems

        """
        rlist = list()
        child, cookie = self.GetFirstChild(parent)
        if not child or not child.IsOk():
            return rlist

        rlist.append(child)
        while True:
            child, cookie = self.GetNextChild(parent, cookie)
            if not child or not child.IsOk():
                return rlist
            rlist.append(child)
        return rlist

    def GetSelectedFiles(self):
        """Get a list of the selected files
        @return: list of strings

        """
        nodes = self.GetSelections()
        files = [ self.GetPyData(node) for node in nodes ]
        return files

    def SelectFile(self, filename):
        """Select the given path
        @param path: full path to select
        @return: bool

        """
        bSelected = False
        # Find the root
        for node in self.GetChildNodes(self.RootItem):
            dname = self.GetPyData(node)
            if not os.path.isdir(dname):
                dname = os.path.dirname(dname)
            if not dname.endswith(os.sep):
                dname += os.sep
            if filename.startswith(dname):
                filename = filename[len(dname):].split(os.sep)
                if not self.IsExpanded(node):
                    self.Expand(node)
                folder = node
                try:
                    while filename:
                        name = filename.pop(0)
                        for item in self.GetChildNodes(folder):
                            if self.GetItemText(item) == name:
                                if not self.IsExpanded(item):
                                    self.Expand(item)
                                folder = item
                                continue
                except:
                    pass

                self.UnselectAll()
                self.EnsureVisible(folder)
                self.SelectItem(folder)
                break

    #---- Static Methods ----#

    @staticmethod
    def GetDirContents(directory):
        """Get the list of files contained in the given directory"""
        assert os.path.isdir(directory)
        files = list()
        try:
            for p in os.listdir(directory):
                files.append(os.path.join(directory, p))
        except OSError:
            pass
        return files

#-----------------------------------------------------------------------------#
# Test
if __name__ == '__main__':
    app = wx.App(False)
    f = wx.Frame(None)
    ft = FileTree(f)
    d = wx.GetUserHome()
    ft.AddWatchDirectory(d)
    f.Show()
    app.MainLoop()
