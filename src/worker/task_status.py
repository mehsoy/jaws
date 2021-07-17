#!/usr/bin/python
#-*- coding: utf-8 -*-

from enum import Enum

class TaskStatus(Enum):
    INITIALIZED = 1
    COPYING = 2
    COPIED = 3
    CHECKED = 4
    DELETED = 5
    FINISHED = 6
    PAUSED = 7
    TERMINATED = 8
    EXCEPTION = 9
    ERROR = 10 
