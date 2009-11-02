###############################################################################
# Name: testArtProvider.py                                                    #
# Purpose: Unit tests for the ArtProvider                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the artprovider"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: testArtProvider.py 61521 2009-07-25 02:30:17Z CJP $"
__revision__ = "$Revision: 61521 $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import unittest

# Local modules
import common

# Module to test
import ed_glob
import ed_art

#-----------------------------------------------------------------------------#
# Test Class

class ArtProviderTest(unittest.TestCase):
    """Tests the ArtProvider class"""
    def setUp(self):
        self.app = common.EdApp(False)
        ap = ed_art.EditraArt()
        wx.ArtProvider.Push(ap)

    def tearDown(self):
        self.app.Exit()

    #---- Test Cases ----#

    def testGetBitmap(self):
        """Test getting a bitmap from the provider"""
        ap = wx.ArtProvider()
        bmp = ap.GetBitmap(str(ed_glob.ID_COPY), wx.ART_MENU)
        self.assertTrue(bmp.IsOk())

        bmp = ap.GetBitmap(str(ed_glob.ID_COPY), wx.ART_TOOLBAR)
        self.assertTrue(bmp.IsOk())

        bmp = ap.GetBitmap(str(-1), wx.ART_MENU)
        self.assertTrue(bmp.IsNull())
