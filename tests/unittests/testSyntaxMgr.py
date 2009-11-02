###############################################################################
# Name: testSyntaxMgr.py                                                      #
# Purpose: Unit tests for the SyntaxMgr                                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for the SyntaxMgr"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: testSyntaxMgr.py 62513 2009-10-31 04:48:39Z CJP $"
__revision__ = "$Revision: 62513 $"

#-----------------------------------------------------------------------------#
# Imports
import unittest

# Module to test
import syntax.syntax as syntax
import syntax.synglob as synglob
import syntax.syndata as syndata

#-----------------------------------------------------------------------------#
# Test Class

class SyntaxMgrTest(unittest.TestCase):

    def setUp(self):
        self.mgr = syntax.SyntaxMgr()
        self.mgr.LoadModule('_python')

    def tearDown(self):
        pass

    #---- Test Cases ----#

    def testSingleton(self):
        """Test that only a singelton instance is created"""
        self.assertTrue(self.mgr is syntax.SyntaxMgr())

    def testGetLangId(self):
        """Test fetching the filetype id associated with the given extension"""
        lid = self.mgr.GetLangId('py')
        self.assertEquals(lid, synglob.ID_LANG_PYTHON)

    def testIsModLoaded(self):
        """Test checking if a module is already loaded"""
        self.assertTrue(self.mgr.IsModLoaded('_python'))
        self.assertFalse(self.mgr.IsModLoaded('_xml'))

    def testLoadModule(self):
        """Test loading a module"""
        self.assertTrue(self.mgr.LoadModule('_cpp'))
        self.assertFalse(self.mgr.LoadModule('_zzz'))

    def testSaveState(self):
        # TODO: use a config in the temp directory
        pass

    def testSyntaxData(self):
        """Test getting the syntax data"""
        data = self.mgr.GetSyntaxData('html')
        self.assertTrue(isinstance(data, syndata.SyntaxDataBase))
        self.assertTrue(isinstance(data.Lexer, int))
        kw = data.Keywords
        self.assertTrue(isinstance(kw, list))
        self.assertTrue(isinstance(kw[0], tuple))
        spec = data.SyntaxSpec
        self.assertTrue(isinstance(spec, list))
        self.assertTrue(isinstance(spec[0], tuple))
        self.assertTrue(isinstance(spec[0][0], int))
        props = data.Properties
        self.assertTrue(isinstance(props, list))
        lang = data.LangId
        self.assertTrue(isinstance(lang, int))
        comment = data.CommentPattern
        self.assertTrue(isinstance(comment, list))
        self.assertTrue(isinstance(comment[0], basestring))

