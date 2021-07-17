#!/usr/bin/python
#-*- coding: utf-8 -*-

class ConfigurationException(Exception):
    def __init__(self, wrong_value, source = ''):
      self._wrong_value = wrong_value
      message = wrong_value + ' has unacceptable value in ' + source + ' configuration file'
      super(ConfigurationException, self).__init__(message) 
      
