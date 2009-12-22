###############################################################################
# Name: ed_editv.py                                                           #
# Purpose: Editor view notebook tab implementation                            #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Text editor buffer view control for the main notebook

@summary: Editor view

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ed_editv.py 62918 2009-12-17 20:29:00Z CJP $"
__revision__ = "$Revision: 62918 $"

#--------------------------------------------------------------------------#
# Imports
import wx
import os

# Editra Libraries
import ed_glob
import ed_menu
import ed_msg
import ed_stc
import ed_tab
from doctools import DocPositionMgr
from profiler import Profile_Get
from util import Log, SetClipboardText
from ebmlib import GetFileModTime

# External libs
from extern.stcspellcheck import STCSpellCheck

#--------------------------------------------------------------------------#

ID_SPELL_1 = wx.NewId()
ID_SPELL_2 = wx.NewId()
ID_SPELL_3 = wx.NewId()

_ = wx.GetTranslation

def modalcheck(func):
    """Decorator method to add extra modality guards to functions that
    show modal dialogs. Arg 0 must be a Window instance.

    """
    def WrapModal(*args, **kwargs):
        """Wrapper method to guard against multiple dialogs being shown"""
        self = args[0]
        self._has_dlg = True
        func(*args, **kwargs)
        self._has_dlg = False

    WrapModal.__name__ = func.__name__
    WrapModal.__doc__ = func.__doc__
    return WrapModal

#--------------------------------------------------------------------------#

class EdEditorView(ed_stc.EditraStc, ed_tab.EdTabBase):
    """Tab editor view for main notebook control."""
    ID_NO_SUGGEST = wx.NewId()
    DOCMGR = DocPositionMgr()
    RCLICK_MENU = None

    def __init__(self, parent, id_=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, use_dt=True):
        """Initialize the editor view"""
        ed_stc.EditraStc.__init__(self, parent, id_, pos, size, style, use_dt)
        ed_tab.EdTabBase.__init__(self)

        # Attributes
        self._ignore_del = False
        self._has_dlg = False
        self._mdata = dict(menu=None, handlers=list(), buff=self)
        self._lprio = 0     # Idle event priority counter
        self._spell = STCSpellCheck(self, check_region=self.IsNonCode)
        spref = Profile_Get('SPELLCHECK', default=dict())
        self._spell_data = dict(choices=list(),
                                word=('', -1, -1),
                                enabled=spref.get('auto', False))

        # Initialize the classes position manager for the first control
        # that is created only.
        if not EdEditorView.DOCMGR.IsInitialized():
            EdEditorView.DOCMGR.InitPositionCache(ed_glob.CONFIG['CACHE_DIR'] + \
                                                  os.sep + u'positions')

        self._spell.clearAll()
        self._spell.setDefaultLanguage(spref.get('dict', 'en_US'))
        self._spell.startIdleProcessing()

        # Context Menu Events
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        # Need to relay the menu events from the context menu to the top level
        # window to be handled on gtk. Other platforms don't require this.
        self.Bind(wx.EVT_MENU, self.OnMenuEvent)

        ed_msg.Subscribe(self.OnConfigMsg,
                         ed_msg.EDMSG_PROFILE_CHANGE + ('SPELLCHECK',))

    def __del__(self):
        ed_msg.Unsubscribe(self.OnConfigMsg)
        super(EdEditorView, self).__del__()

    def _MakeMenu(self, pos):
        """Make the buffers context menu,
        @param pos: mouse click position

        """
        menu = ed_menu.EdMenu()
        menu.Append(ed_glob.ID_UNDO, _("Undo"))
        menu.Append(ed_glob.ID_REDO, _("Redo"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_CUT, _("Cut"))
        menu.Append(ed_glob.ID_COPY, _("Copy"))
        menu.Append(ed_glob.ID_PASTE, _("Paste"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_TO_UPPER, _("To Uppercase"))
        menu.Append(ed_glob.ID_TO_LOWER, _("To Lowercase"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_SELECTALL, _("Select All"))

        # Allow clients to customize the context menu
        self._mdata['menu'] = menu
        self._mdata['handlers'] = list()
        self._mdata['position'] = self.PositionFromPoint(self.ScreenToClient(pos))
        ed_msg.PostMessage(ed_msg.EDMSG_UI_STC_CONTEXT_MENU,
                           self._mdata,
                           self.GetId())

        # Spell checking
        # TODO: de-couple to the forthcoming buffer service interface
        menu.InsertSeparator(0)
        words = self.GetWordFromPosition(self._mdata['position'])
        self._spell_data['word'] = words
        sugg = self._spell.getSuggestions(words[0])

        # Don't give suggestions if the selected word is in the suggestions list
        if words[0] in sugg:
            sugg = list()

        if not len(sugg):
            item = menu.Insert(0, EdEditorView.ID_NO_SUGGEST, _("No Suggestions"))
            item.Enable(False)
        else:
            sugg = reversed(sugg[:min(len(sugg), 3)])
            ids = (ID_SPELL_1, ID_SPELL_2, ID_SPELL_3)
            del self._spell_data['choices']
            self._spell_data['choices'] = list()
            for idx, sug in enumerate(sugg):
                id_ = ids[idx] 
                self._mdata['handlers'].append((id_, self.OnSpelling))
                self._spell_data['choices'].append((id_, sug))
                menu.Insert(0, id_, sug)

        return menu

    #---- EdTab Methods ----#

    def DoDeactivateTab(self):
        """Deactivate any active popups when the tab is no longer
        the active tab.

        """
        if self.AutoCompActive():
            self.AutoCompCancel()

        if self.CallTipActive():
            self.CallTipCancel()

    def DoOnIdle(self):
        """Check if the file has been modified and prompt a warning"""
        # Don't check while the file is loading
        if self.IsLoading():
            return

        if not self._has_dlg and Profile_Get('CHECKMOD'):
            cfile = self.GetFileName()
            lmod = GetFileModTime(cfile)
            mtime = self.GetModTime()
            if mtime and not lmod and not os.path.exists(cfile):
                # File was deleted since last check
                wx.CallAfter(self.PromptToReSave, cfile)
            elif mtime < lmod:
                # Check if we should automatically reload the file or not
                if Profile_Get('AUTO_RELOAD', default=False) and \
                   not self.GetModify():
                    wx.CallAfter(self.DoReloadFile)
                else:
                    wx.CallAfter(self.AskToReload, cfile)

        # Check for changes to permissions
        readonly = self._nb.ImageIsReadOnly(self.GetTabIndex())
        if self.File.IsReadOnly() != readonly:
            if readonly:
                # File is no longer read only
                self._nb.SetPageImage(self.GetTabIndex(),
                                      str(self.GetLangId()))
            else:
                # File has changed to be readonly
                self._nb.SetPageImage(self.GetTabIndex(),
                                      ed_glob.ID_READONLY)
            self._nb.Refresh()

        else:
            pass

        # Handle Low(er) priority idle events
        self._lprio += 1
        if self._lprio == 2:
            self._lprio = 0 # Reset counter
            # Do spell checking
            # TODO: Add generic subscriber hook and move spell checking and
            #       and other low priority idle handling there
            if self._spell_data['enabled']:
                self._spell.processCurrentlyVisibleBlock()

    @modalcheck
    def DoReloadFile(self):
        """Reload the current file"""
        ret, rmsg = self.ReloadFile()
        if not ret:
            cfile = self.GetFileName()
            errmap = dict(filename=cfile, errmsg=rmsg)
            mdlg = wx.MessageDialog(self,
                                    _("Failed to reload %(filename)s:\n"
                                      "Error: %(errmsg)s") % errmap,
                                    _("Error"),
                                    wx.OK | wx.ICON_ERROR)
            mdlg.ShowModal()
            mdlg.Destroy()

    def DoTabClosing(self):
        """Save the current position in the buffer to reset on next load"""
        if len(self.GetFileName()) > 1:
            EdEditorView.DOCMGR.AddRecord([self.GetFileName(),
                                           self.GetCurrentPos()])

    def DoTabOpen(self, ):
        """Called to open a new tab"""
        pass

    def DoTabSelected(self):
        """Performs updates that need to happen when this tab is selected"""
        Log("[ed_editv][info] Tab has file: %s" % self.GetFileName())
        self.PostPositionEvent()

    def GetName(self):
        """Gets the unique name for this tab control.
        @return: (unicode) string

        """
        return u"EditraTextCtrl"

    def GetTabMenu(self):
        """Get the tab menu
        @return: wx.Menu
        @todo: move logic from notebook to here

        """
        ptxt = self.GetTabLabel()

        menu = ed_menu.EdMenu()
        menu.Append(ed_glob.ID_NEW, _("New Tab"))
        menu.Append(ed_glob.ID_MOVE_TAB, _("Move Tab to New Window"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_SAVE, _("Save \"%s\"") % ptxt)
        menu.Append(ed_glob.ID_CLOSE, _("Close \"%s\"") % ptxt)
        menu.Append(ed_glob.ID_CLOSEALL, _("Close All"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_COPY_PATH, _("Copy Full Path"))
        return menu

    def GetTitleString(self):
        """Get the title string to display in the MainWindows title bar
        @return: (unicode) string

        """
        fname = self.GetFileName()
        title = os.path.split(fname)[-1]

        # Its an unsaved buffer
        if not len(title):
            title = fname = self.GetTabLabel()

        if self.GetModify() and not title.startswith(u'*'):
            title = u"*" + title
        return u"%s - file://%s" % (title, fname)

    def CanCloseTab(self):
        """Called when checking if tab can be closed or not
        @return: bool

        """
        if self._ignore_del:
            return True

        result = True
        if self.GetModify():
            # TODO: Move this method down from the frame to here
            result = self.GetTopLevelParent().ModifySave()
            result = result in (wx.ID_YES, wx.ID_OK, wx.ID_NO)

        return result

    def OnSpelling(self, buff, evt):
        """Context menu subscriber callback
        @param buff: buffer menu event happened in
        @param evt: MenuEvent

        """
        e_id = evt.GetId()
        replace = None
        for choice in self._spell_data['choices']:
            if e_id == choice[0]:
                replace = choice[1]
                break

        if replace is not None:
            buff.SetTargetStart(self._spell_data['word'][1])
            buff.SetTargetEnd(self._spell_data['word'][2])
            buff.ReplaceTarget(replace)

    def OnTabMenu(self, evt):
        """Tab menu event handler"""
        e_id = evt.GetId()
        if e_id == ed_glob.ID_COPY_PATH:
            path = self.GetFileName()
            if path is not None:
                SetClipboardText(path)
        elif e_id == ed_glob.ID_MOVE_TAB:
            frame = wx.GetApp().OpenNewWindow()
            nbook = frame.GetNotebook()
            parent = self.GetParent()
            pg_txt = parent.GetRawPageText(parent.GetSelection())
            nbook.OpenDocPointer(self.GetDocPointer(),
                                 self.GetDocument(), pg_txt)
            self._ignore_del = True
            wx.CallAfter(parent.ClosePage)
        elif wx.Platform == '__WXGTK__' and \
             e_id in (ed_glob.ID_CLOSE, ed_glob.ID_CLOSEALL):
            # Need to relay events up to toplevel window on GTK for them to
            # be processed. On other platforms the propagate by them selves.
            wx.PostEvent(self.GetTopLevelParent(), evt)
        else:
            evt.Skip()

    #---- End EdTab Methods ----#

    def IsNonCode(self, pos):
        """Is the passed in position in a non code region
        @param pos: buffer position
        @return: bool

        """
        return self.IsComment(pos) or self.IsString(pos)

    def OnConfigMsg(self, msg):
        """Update config based on profile changes"""
        mtype = msg.GetType()
        mdata = msg.GetData()
        if mtype[-1] == 'SPELLCHECK':
            self._spell_data['enabled'] = mdata.get('auto', False)
            self._spell.setDefaultLanguage(mdata.get('dict', 'en_US'))
            if not self._spell_data['enabled']:
                self._spell.clearAll()

    def OnContextMenu(self, evt):
        """Handle right click menu events in the buffer"""
        if EdEditorView.RCLICK_MENU is not None:
            EdEditorView.RCLICK_MENU.Destroy()
            EdEditorView.RCLICK_MENU = None

        EdEditorView.RCLICK_MENU = self._MakeMenu(evt.GetPosition())
        self.PopupMenu(EdEditorView.RCLICK_MENU)
        evt.Skip()

    def OnMenuEvent(self, evt):
        """Handle context menu events"""
        e_id = evt.GetId()
        handler = None
        for hndlr in self._mdata['handlers']:
            if e_id == hndlr[0]:
                handler = hndlr[1]
                break

        # Handle custom menu items
        if handler is not None:
            handler(self, evt)
        else:
            # Need to relay to tlw on gtk for it to get handled, other
            # platforms do not require this.
            if wx.Platform == '__WXGTK__':
                wx.PostEvent(self.GetTopLevelParent(), evt)
            else:
                evt.Skip()

    def OnModified(self, evt):
        """Overrides EditraBaseStc.OnModified"""
        super(EdEditorView, self).OnModified(evt)

        # Handle word changes to update spell checking
        # TODO: limit via preferences and move to buffer service once
        #       implemented.
        mod = evt.GetModificationType() 
        if mod & wx.stc.STC_MOD_INSERTTEXT or mod & wx.stc.STC_MOD_DELETETEXT: 
            pos = evt.GetPosition() 
            last = pos + evt.GetLength() 
            self._spell.addDirtyRange(pos, last, evt.GetLinesAdded(),
                                      mod & wx.stc.STC_MOD_DELETETEXT) 

    @modalcheck
    def PromptToReSave(self, cfile):
        """Show a dialog prompting to resave the current file
        @param cfile: the file in question

        """
        mdlg = wx.MessageDialog(self,
                                _("%s has been deleted since its "
                                  "last save point.\n\nWould you "
                                  "like to save it again?") % cfile,
                                _("Resave File?"),
                                wx.YES_NO | wx.ICON_INFORMATION)
        mdlg.CenterOnParent()
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_YES:
            result = self.SaveFile(cfile)
        else:
            self.SetModTime(0)

    @modalcheck
    def AskToReload(self, cfile):
        """Show a dialog asking if the file should be reloaded
        @param cfile: the file to prompt for a reload of

        """
        mdlg = wx.MessageDialog(self,
                                _("%s has been modified by another "
                                  "application.\n\nWould you like "
                                  "to reload it?") % cfile,
                                  _("Reload File?"),
                                  wx.YES_NO | wx.ICON_INFORMATION)
        mdlg.CenterOnParent()
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_YES:
            self.DoReloadFile()
        else:
            self.SetModTime(GetFileModTime(cfile))

    def SetLexer(self, lexer):
        """Override to toggle spell check context"""
        super(EdEditorView, self).SetLexer(lexer)

        if lexer == wx.stc.STC_LEX_NULL:
            self._spell.setCheckRegion(lambda p: True)
        else:
            self._spell.setCheckRegion(self.IsNonCode)

#-----------------------------------------------------------------------------#
