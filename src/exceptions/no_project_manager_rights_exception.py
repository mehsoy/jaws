#!/usr/bin/python
#-*- coding: utf-8 -*-

from .permission_exception import PermissionException

class NoProjectManagerRightsException(PermissionException):
    pass
