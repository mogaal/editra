###############################################################################
# Name: ed_fmgr.py                                                            #
# Purpose: Editra's Main Window Frame Manager                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""


"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependencies
import wx
import wx.aui as aui

#--------------------------------------------------------------------------#

class EdFrameManager(aui.AuiManager):
    """Frame manager for external components to abstract underlying manager"""
    def __init__(self, wnd=None, flags=0):
        """Create the frame manager object
        @param wnd: Frame to manage
        @param flags: frame manager flags

        """
        super(EdFrameManager, self).__init__(wnd, flags)

    def AddPane(self, wnd, info=None, caption=None):
        return super(EdFrameManager, self).AddPane(wnd, info, caption)

    def IsEditorMaximized(self):
        """Is the editor pane maximized?
        return: bool

        """
        bEditMax = True
        # If any other pane is open then the editor is not maximized
        for pane in self.GetAllPanes():
            if pane.IsShown() and pane.name != "EditPane":
                bEditMax = False
                break
        return bEditMax

#--------------------------------------------------------------------------#

EdPaneInfo = aui.AuiPaneInfo
#    """Frame manager panel info"""
#    def __init__(self):
#        super(EdPaneInfo, self).__init__()
