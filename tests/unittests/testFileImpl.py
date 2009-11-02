###############################################################################
# Name: testFileImpl.py                                                       #
# Purpose: Unit tests for FileObjectImpl                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittests for ebmlib.FileObjectImpl class"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: testFileImpl.py 61504 2009-07-23 03:39:28Z CJP $"
__revision__ = "$Revision: 61504 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import types
import unittest

# Local unittest imports
import common

# Module(s) to test
import ebmlib

#-----------------------------------------------------------------------------#

class FileImplTest(unittest.TestCase):
    def setUp(self):
        self.path = common.GetDataFilePath(u'test_read_utf8.txt')
        self.file = ebmlib.FileObjectImpl(self.path)
        self.mtime = ebmlib.GetFileModTime(self.path)

    def tearDown(self):
        self.file.Close()

    #---- Tests ----#

    def testClone(self):
        """Test cloning the file object"""
        fobj = self.file.Clone()
        self.assertTrue(fobj.GetPath() == self.file.GetPath())
        self.assertTrue(fobj.GetModtime() == self.file.GetModtime())
        self.assertTrue(fobj.IsReadOnly() == self.file.IsReadOnly())

    def testRead(self):
        """Test reading from the file and getting the text"""
        txt = self.file.Read()
        self.assertTrue(len(txt))

    def testExists(self):
        """Test if the file exists"""
        self.assertTrue(self.file.Exists())
        nfile = ebmlib.FileObjectImpl('some_fake_file')
        self.assertFalse(nfile.Exists())

    def testGetExtension(self):
        """Test getting the file extension"""
        self.assertTrue(self.file.GetExtension() == 'txt')

    def testGetLastError(self):
        """Test fetching last file op error"""
        self.assertEquals(self.file.GetLastError(), u"None")

    def testGetPath(self):
        """Test getting the files path"""
        self.assertTrue(self.file.GetPath() == self.path)

    def testGetModTime(self):
        """Test getting the files last modification time"""
        self.file.SetModTime(self.mtime)
        mtime = self.file.GetModtime()
        self.assertTrue(mtime == self.mtime, "Modtime was: " + str(mtime))
        self.assertTrue(mtime == self.file.Modtime)

    def testIsOpen(self):
        """Test checking the state of the file"""
        self.assertFalse(self.file.IsOpen())

    def testIsReadOnly(self):
        """Test if the file is read only or not"""
        self.assertFalse(self.file.IsReadOnly(), "File is readonly")
        self.assertEqual(self.file.IsReadOnly(), self.file.ReadOnly)

    def testGetSize(self):
        """Test fetching the file size"""
        self.assertTrue(self.file.GetSize() > 0)
