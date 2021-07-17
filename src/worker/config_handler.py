#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import toml
import json

from helpers import Singleton
from worker.conf_schemata import validate_general

from exceptions.incorrect_config_file_error import IncorrectConfigFileError


class ConfigHandler(metaclass=Singleton):
    """Reads configuration file for Worker package"""

    def __init__(self, config_path):
        if not os.path.exists(config_path):
            raise IncorrectConfigFileError('Configuration file not found')

        self._config = toml.load(config_path)

        general_section = validate_general(self._config.pop('general'))
        self._worker_name = general_section['worker_name']
        self._worker_address = general_section['worker_address']
        self._master_address = general_section['master_address']
        self._authentification_token = general_section['authentification_token']
        self._reconnect_timeout = general_section['reconnect_timeout']
        self._reconnect_frequency = general_section['reconnect_frequency']
        self.mountpoints = general_section['mountpoints']

    def get_worker_name(self):
        return self._worker_name

    def get_authentification_token(self):
        return self._authentification_token

    def get_worker_address(self):
        return self._worker_address

    def get_master_address(self):
        return self._master_address

    def get_reconnect_timeout(self):
        return self._reconnect_timeout

    def get_reconnect_frequency(self):
        return self._reconnect_frequency

    def get_mountpoints(self):
        return self.mountpoints
