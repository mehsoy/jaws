#!/usr/bin/python
#-*- coding: utf-8 -*-

from enum import Enum

class WorkerStatus(Enum):
    ACTIVE = 1
    WAITING = 2
    PAUSED = 3
    DEACTIVATED = 4
