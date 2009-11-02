###############################################################################
# Name: miscutil.py                                                           #
# Purpose: Various helper functions.                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Buisness Model Library: MiscUtil

Various helper functions

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: miscutil.py 60840 2009-05-31 16:00:50Z CJP $"
__revision__ = "$Revision: 60840 $"

__all__ = [ 'MinMax', ]

#-----------------------------------------------------------------------------#
# Imports

#-----------------------------------------------------------------------------#

def MinMax(arg1, arg2):
    """Return an ordered tuple of the minumum and maximum value
    of the two args.
    @return: tuple

    """
    return min(arg1, arg2), max(arg1, arg2)
