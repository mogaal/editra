###############################################################################
# Name: _dirmon.py                                                            #
# Purpose: Directory monitor object.                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Business Model Library: DirectoryMonitor


"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: _dirmon.py 70229 2012-01-01 01:27:10Z CJP $"
__revision__ = "$Revision: 70229 $"

__all__ = ['DirectoryMonitor',]

#-----------------------------------------------------------------------------#
# Imports
import wx
import os
import time
import threading

# Local imports
import fileutil

#-----------------------------------------------------------------------------#

class DirectoryMonitor(object):
    """Object to manage monitoring file system changes"""
    def __init__(self):
        super(DirectoryMonitor, self).__init__()

        # Attributes
        self._watcher = WatcherThread(self._ThreadNotifier)
        self._callbacks = list()
        self._cbackLock = threading.Lock()
        self._running = False

    def __del__(self):
        if self._running:
            self._watcher.Shutdown()
            self._watcher.join()

    def _ThreadNotifier(self, added, deleted, modified):
        """Notifier callback from background L{WatcherThread}
        to call notifiers on main thread.
        @note: this method is invoked from a background thread and
               is not safe to make direct UI calls from.

        """
        with self._cbackLock:
            for cback in self._callbacks:
                wx.CallAfter(cback, added, deleted, modified)

    #---- Properties ----#

    # Is the monitor currently watching any directories
    Monitoring = property(lambda self: self._running)

    #---- End Properties ----#

    def AddDirectory(self, dname):
        """Add a directory to the monitor
        @param dname: directory path

        """
        self._watcher.AddWatchDirectory(dname)

    def SubscribeCallback(self, callback):
        """Subscribe a callback method to be called when changes are
        detected in one of the watched directories.
        @param callback: callable([added,], [deleted,], [modified,])

        """
        with self._cbackLock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)

    def UnsubscribeCallback(self, callback):
        """Remove a callback method from the monitor"""
        with self._cbackLock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def RemoveDirectory(self, dname):
        """Remove a directory from the watch list
        @param dname: directory path

        """
        self._watcher.RemoveWatchDirectory(dname)

    def StartMonitoring(self):
        """Start monitoring the directories in the watch list and
        notifying target of changes.

        """
        self._running = True
        self._watcher.start()

#-----------------------------------------------------------------------------#
    
class WatcherThread(threading.Thread):
    """Background thread to monitor a directory"""
    def __init__(self, notifier):
        """Create the WatcherThread. Provide a callback notifier method
        that will be called when changes are detected in the directory.
        The notifier will be called in the context of this thread. Notifier
        will be called with three lists of ebmlib.File objects to indicate
        the changes that have occurred.
        @param notifier: callable([added,], [deleted,], [modified,])

        """
        super(WatcherThread, self).__init__()

        # Attributes
        assert callable(notifier)
        self._notifier = notifier
        self._dirs = list() # Directories being monitored

        self._freq = 1000.0 # Monitoring frequency in milliseconds
        self._continue = True
        self._lock = threading.Lock()
        self._suspend = False
        self._suspendcond = threading.Condition()

    def run(self):
        """Run the watcher"""
        # TODO: wait on condition/event when dir list is empty
        #       instead of looping per frequency interval.
        while self._continue:
            deleted = list()
            added = list()
            modified = list()

            # Suspend processing if requested
            if self._suspend:
                with self._suspendcond:
                    self._suspendcond.wait()

            with self._lock:
                for dobj in self._dirs:
                    if not self._continue:
                        return

                    # Check if a watched directory has been deleted
                    if not os.path.exists(dobj.Path):
                        deleted.append(dobj)
                        self._dirs.remove(dobj)
                        continue

                    snapshot = fileutil.GetDirectoryObject(dobj.Path, 
                                                           False, True)

                    # Check for deletions
                    for tobj in dobj.Files:
                        if not self._continue:
                            return
                        if tobj not in snapshot.Files:
                            deleted.append(tobj)
                            dobj.Files.remove(tobj)

                    # Check for additions and modifications
                    for tobj in snapshot.Files:
                        if not self._continue:
                            return
                        if tobj not in dobj.Files:
                            # new object was added
                            added.append(tobj)
                            dobj.Files.append(tobj)
                        else:
                            idx = dobj.Files.index(tobj)
                            existing = dobj.Files[idx]
                            # object was modified
                            if existing.ModTime < tobj.ModTime:
                                modified.append(tobj)
                                existing.ModTime = tobj.ModTime

            # Call Notifier if anything changed
            if any((added, deleted, modified)):
                self._notifier(added, deleted, modified)

            # Wait till next check
            time.sleep(self._freq / 1000.0)

    #---- Implementation ----#

    def AddWatchDirectory(self, dpath):
        """Add a directory to the watch list
        @param dpath: directory path (unicode)

        """
        assert os.path.isdir(dpath)
        dobj = fileutil.Directory(dpath)
        with self._lock:
            if dobj not in self._dirs:
                # Get current snapshot of the directory
                dobj = fileutil.GetDirectoryObject(dpath, False, True)
                self._dirs.append(dobj)

    def RemoveWatchDirectory(self, dpath):
        """Remove a directory from the watch
        @param dpath: directory path to remove (unicode)

        """
        dobj = fileutil.Directory(dpath)
        with self._lock:
            if dobj in self._dirs:
                self._dirs.remove(dobj)

    def SetFrequency(self, milli):
        """Set the update frequency
        @param milli: int (milliseconds)

        """
        self._freq = float(milli)

    def Shutdown(self):
        """Shut the thread down"""
        self._continue = False

    def Suspend(self):
        """Suspend the thread"""
        self._suspend = True

    def Continue(self):
        """Continue the thread"""
        self._suspend = False
        with self._suspendcond:
            self._suspendcond.notify()
