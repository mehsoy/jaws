#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import configparser
from exceptions.configuration_exception import ConfigurationException
from exceptions.incorrect_config_file_error import IncorrectConfigFileError

class ConfigHandler:
    def __init__(self, config_file):
      """The Constructor"""   
      if not os.path.exists(config_file):
        raise IncorrectConfigFileError('Configuration file not found')
      if not (config_file[-4:] == ".ini") :
        raise IncorrectConfigFileError('Configuration file is in the wrong format')
      self._configuration_file = config_file
      _config = configparser.ConfigParser()
      _config.read(self._configuration_file)
      self._config_parser = _config
      
      self._token = _config.get('General Configuration', 'token')
      self._address = _config.get('General Configuration', 'master_address')

      try: 
        self._active_on_start = _config.getboolean('General Configuration', 'active_on_start')
      except ValueError as exc:
       raise ConfigurationException('active on start') from exc
    
    def get_address(self):
        return self._address

    def get_communicator_port(self):
        return self._address.split(':')[1]

    def get_token(self):
      """Returns token for the authentifikation at workers"""
      return self._token

    def get_active_on_start(self):
      """Returns whether master accepts jobs immediately after start or if the activate method has to be called"""
      return self._active_on_start



