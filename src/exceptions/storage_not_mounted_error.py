#!/usr/bin/python
#-*- coding: utf-8 -*-

from .worker_setting_fail_exception import WorkerSettingFailException


class StorageNotMountedError(WorkerSettingFailException):
    def __init__(self, location=None, mountpoint=None):
        NO_MOUNT = "The Storage with the and mountpath '%s' is not mounted in %s."
        self.message = NO_MOUNT % (mountpoint, location)
        super(StorageNotMountedError, self).__init__(self.message)
