###############################################################################
# Name: testEBMClipboard.py                                                   #
# Purpose: Unit tests for ebmlib.Clipboard                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing the ebmlib.Clipboard"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: testEBMClipboard.py 63851 2010-04-04 15:39:50Z CJP $"
__revision__ = "$Revision: 63851 $"

#-----------------------------------------------------------------------------#
# Imports
import unittest
import wx

# Module to test
import ebmlib

#-----------------------------------------------------------------------------#
# Test Class

class EBMClipboardTest(unittest.TestCase):

    def setUp(self):
        # All methods are class methods
        self.cb = ebmlib.Clipboard

    def tearDown(self):
        self.cb.Switch('"') # Switch back to default (system clipboard)
        self.cb.DeleteAll() # Delete all clipboard registers

    def testSwitch(self):
        self.assertRaises(ebmlib.ClipboardException, self.cb.Switch, 1)
        self.cb.Switch('m')
        self.cb.Set("HELLO")
        val = self.cb.Get()
        self.assertEquals(val, "HELLO")
        self.cb.Switch('n')
        val = self.cb.Get()
        self.assertEquals(val, u'')

    def testNextFree(self):
        self.cb.NextFree()
        self.assertEquals(self.cb.current, u'a')
        self.cb.Set("TEST")
        self.cb.NextFree()
        self.assertEquals(self.cb.current, u'b')

    def testAllUsed(self):
        used = self.cb.AllUsed()
        self.assertTrue(len(used) == 1)
        self.cb.NextFree()
        self.cb.Set("Test1")
        self.cb.NextFree()
        self.cb.Set("Test2")
        used = self.cb.AllUsed()
        self.assertTrue('"' in used)
        self.assertTrue('a' in used)
        self.assertTrue('b' in used)
        
    def testGetSet(self):
        self.cb.Switch("a")
        self.cb.Set("Foo")
        val = self.cb.Get()
        self.assertTrue(val == "Foo")

