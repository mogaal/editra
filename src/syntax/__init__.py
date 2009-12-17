###############################################################################
# Name: __init__.py                                                           #
# Purpose: initialize the syntax package                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################
"""Syntax data package

Provides:
  - Keyword Data
  - Syntax styling definitions

For all differn't file types and languages supported by Editra

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: __init__.py 62572 2009-11-08 19:16:11Z CJP $"
__revision__ = "$Revision: 62572 $"

#-----------------------------------------------------------------------------#
# Setup Namespace

from synxml import *
from synglob import GetIdFromDescription, GetDescriptionFromId

#-----------------------------------------------------------------------------#