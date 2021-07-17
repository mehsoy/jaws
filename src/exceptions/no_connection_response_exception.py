#!/usr/bin/python
#-*- coding: utf-8 -*-

from .worker_setting_fail_exception import WorkerSettingFailException
from .storage_access_exception import StorageAccessException

class NoConnectionResponseException(WorkerSettingFailException, StorageAccessException):
    pass
