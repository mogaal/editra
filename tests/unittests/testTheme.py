###############################################################################
# Name: testTheme.py                                                          #
# Purpose: Unit tests for the Icon Theme provider                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the icon theme provider interface"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: testTheme.py 61520 2009-07-25 02:08:49Z CJP $"
__revision__ = "$Revision: 61520 $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import unittest

# Local modules
import common

# Module to test
import ed_glob
import ed_theme

#-----------------------------------------------------------------------------#
# Test Class

class ThemeTest(unittest.TestCase):
    """Tests the BitmapProvier class"""
    def setUp(self):
        ed_glob.CONFIG['THEME_DIR'] = common.GetThemeDir()
        self.app = common.EdApp(False)
        pmgr = self.app.GetPluginManager()
        self.bmpprov = ed_theme.BitmapProvider(pmgr)

    def tearDown(self):
        self.app.Exit()

    #---- Test Cases ----#

    def testGetThemes(self):
        """Test getting the list of available themes"""
        themes = self.bmpprov.GetThemes()

        # Should return a list
        self.assertTrue(isinstance(themes, list))

        # Should be at least one
        self.assertTrue(len(themes))

    def testGetBitmap(self):
        """Test retrieving a bitmap from the theme
        GetBitmap(self, bmp_id, client)

        """
        bmp = self.bmpprov.GetBitmap(ed_glob.ID_COPY, wx.ART_MENU)
        self.assertTrue(bmp.IsOk(), repr(bmp))
        self.assertEquals(bmp.GetSize(), wx.Size(16,16))

        # Try for non existant bitmap
        bmp = self.bmpprov.GetBitmap(-1, wx.ART_MENU)
        self.assertTrue(bmp.IsNull())
