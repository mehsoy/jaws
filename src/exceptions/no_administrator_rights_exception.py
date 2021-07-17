#!/usr/bin/python
#-*- coding: utf-8 -*-

from .permission_exception import PermissionException

class NoAdministratorRightsException(PermissionException):
    pass
