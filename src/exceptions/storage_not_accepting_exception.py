#!/usr/bin/python
#-*- coding: utf-8 -*-

from .storage_access_exception import StorageAccessException

class StorageNotAcceptingException(StorageAccessException):
    pass
