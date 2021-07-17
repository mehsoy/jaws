#!/usr/bin/python
#-*- coding: utf-8 -*-

class SystemSetupError(EnvironmentError):
    def __init__(self, msg: str):
        self.output = msg
