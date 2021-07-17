#!/usr/bin/python
#-*- coding: utf-8 -*-

from .storage_access_exception import StorageAccessException

class StorageNotMountedException(StorageAccessException):
    pass
