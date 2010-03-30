###############################################################################
# Name: filterdlg.py                                                          #
# Purpose: Filter dialog                                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Editra Control Library: FilterDialog


"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: filterdlg.py 63200 2010-01-20 03:49:01Z CJP $"
__revision__ = "$Revision: 63200 $"

__all__ = ["FilterDialog",]

#-----------------------------------------------------------------------------#
# Imports
import wx

# Eclib Imports
import ecbasewin

#-----------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class FilterDialog(ecbasewin.ECBaseDlg):
    """Dialog that allows adding and removing items from a filter list"""
    def __init__(self, parent, id=wx.ID_ANY, title=u"",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.DEFAULT_DIALOG_STYLE, name=u"FilterDialog"):
        ecbasewin.ECBaseDlg.__init__(self, parent, id, title,
                                     pos, size, style, name)

        # Attributes
        self.SetPanel(FilterPanel(self))

        # Event Handlers

#-----------------------------------------------------------------------------#

class FilterPanel(wx.Panel):
    """Filter dialog panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes
        self._left  = wx.ListBox(self, style=wx.LB_MULTIPLE|wx.LB_SORT)
        self._right = wx.ListBox(self, style=wx.LB_MULTIPLE)

        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        
    def __DoLayout(self):
        """Layout the panel"""
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        hsizer.Add(self._left, 1, wx.EXPAND|wx.ALL, 10)

        # Add buttons
        bvsizer = wx.BoxSizer(wx.VERTICAL)
        addb = wx.Button(self, wx.ID_ADD, label=_("Add >>"))
        removeb = wx.Button(self, wx.ID_REMOVE, label=_("<< Remove"))
        bvsizer.AddStretchSpacer()
        bvsizer.AddMany([(addb, 0, wx.EXPAND),
                         ((10, 15), 0),
                         (removeb, 0, wx.EXPAND)])
        bvsizer.AddStretchSpacer()

        hsizer.Add(bvsizer, 0, wx.ALIGN_CENTER)
        hsizer.Add(self._right, 1, wx.EXPAND|wx.ALL, 10)

        vsizer.Add(hsizer, 1, wx.EXPAND)

        # Add main dialog buttons
        bsizer = wx.StdDialogButtonSizer()
        bsizer.AddButton(wx.Button(self, wx.ID_OK))
        btn = wx.Button(self, wx.ID_CANCEL)
        bsizer.AddButton(btn)
        btn.SetDefault()
        bsizer.Realize()
        vsizer.Add(bsizer, 0, wx.ALIGN_RIGHT)
        vsizer.AddSpacer(8)

        self.SetSizer(vsizer)
        self.SetAutoLayout(True)

    @ecbasewin.expose(FilterDialog)
    def GetIncludes(self):
        """Get the items from the includes list
        @return: list of strings

        """
        return self._right.GetItems()

    @ecbasewin.expose(FilterDialog)
    def SetIncludes(self, items):
        """Set the items in the includes list
        @param items: list of strings

        """
        return self._right.SetItems(items)

    @ecbasewin.expose(FilterDialog)
    def GetExcludes(self):
        """Get the items from the excludes list
        @return: list of strings

        """
        return self._left.GetItems()

    @ecbasewin.expose(FilterDialog)
    def SetExcludes(self, items):
        """set the items in the excludes list
        @param items: list of strings

        """
        return self._left.SetItems(items)

    @ecbasewin.expose(FilterDialog)
    def SetListValues(self, valuemap):
        """Set the values of the filter lists
        @param valuemap: dict(item=bool)

        """
        includes = list()
        excludes = list()
        for item, include in valuemap.iteritems():
            if include:
                includes.append(item)
            else:
                excludes.append(item)
        includes.sort()
        excludes.sort()
        self.SetIncludes(includes)
        self.SetExcludes(excludes)

    def OnButton(self, evt):
        e_id = evt.GetId()
        if e_id in (wx.ID_ADD, wx.ID_REMOVE):
            cmap = { wx.ID_ADD : (self._left, self._right),
                     wx.ID_REMOVE : (self._right, self._left) }
            idxs = list()
            for sel in cmap[e_id][0].GetSelections():
                selstr = cmap[e_id][0].GetString(sel)
                cmap[e_id][1].Append(selstr)
                idxs.append(sel)
            idxs.sort()
            idxs.reverse()
            for idx in idxs:
                cmap[e_id][0].Delete(idx)
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    app = wx.App(False)
    dlg = FilterDialog(None, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    dlg.SetListValues(dict(apple=True, orange=False,
                           banana=False, peach=False,
                           mango=True, strawberry=False))
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()

