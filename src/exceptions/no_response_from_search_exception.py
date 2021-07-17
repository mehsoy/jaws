#!/usr/bin/python
#-*- coding: utf-8 -*-

from .connection_exception import ConnectionException

class NoResponseFromSearchException(ConnectionException):
    pass
