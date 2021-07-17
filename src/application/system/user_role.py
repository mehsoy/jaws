#!/usr/bin/python
#-*- coding: utf-8 -*-

from enum import Enum


class UserRole(Enum):
    User = 'User'
    ProjectManager = 'ProjectManager'
    Administrator = 'Administrator'


