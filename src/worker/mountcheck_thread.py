#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import threading
import queue

from worker.config_handler import ConfigHandler
from exceptions.storage_not_mounted_error import StorageNotMountedError

class MountcheckThread(threading.Thread):
    """
    Threadclass made specifically for checking whether storages are mounted.

    :raises StorageNotMontedError: If a Storage is not mounted at its given mountpath.
    """

    def __init__(self, bucket: queue.Queue, path):
        """
        Constructor of the class.

        :param bucket: queue where possible errors are put in order to get them in the main thread
        :param storage: storage which mountpoint is to be checked
        """
        threading.Thread.__init__(self)
        self.bucket = bucket
        self.path = path

    def run(self):
        try:
            if not (os.path.ismount(self.path)):
                raise StorageNotMountedError(ConfigHandler().get_worker_name(), self.path)
        except StorageNotMountedError:
            self.bucket.put(sys.exc_info())

def is_mounted(path):
    """
    Return True if mount_path of given Storage is a mount point: a point
    in a file system where a
    different file system has been mounted.

    :param path: the path to be checked for mount.
    """
    # same solution as in search
    bucket = queue.Queue()
    new_thread = MountcheckThread(bucket, path)
    new_thread.start()
    new_thread.join(10)
    try:
        exc = bucket.get(block=False)
        exc_type, exc_obj, exc_trace = exc
        if exc:
            if exc_type is StorageNotMountedError:
                return False
            else:
                raise exc_obj
    except queue.Empty:
        pass
    if new_thread.isAlive():
        raise Exception("Timeout for checking mountpoints was exceeded.")
    return True