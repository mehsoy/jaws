#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import queue

from flask import Flask

from helpers import unmunge_request, munge_response
from worker.blueprints.api import blueprint as api
from worker.config_handler import ConfigHandler

from worker.tool_config_parser import ToolConfigParser
from worker.worker_class import Worker
from worker.msg_out import Out
from worker.msg_in import MsgIn
from worker.mountcheck_thread import MountcheckThread, is_mounted

from exceptions.storage_not_mounted_error import StorageNotMountedError
from exceptions.configuration_exception import ConfigurationException
from exceptions.incorrect_config_file_error import IncorrectConfigFileError


class WorkerInitializer:
    def __init__(self, config_path: str, copytool_path: str):
        if not os.path.exists(config_path):
            raise (IncorrectConfigFileError("No file was found at " + config_path))

        self._storagedict = dict()  # Contains key value dict for each key(i.e. alias)
        self._storages = dict()  # Contains actual storages for each key(i.e. alias)
        self.parse_configfile(config_path)
        self.create_objects()
        # Create singleton object for future use
        ToolConfigParser(copytool_path)

    def parse_configfile(self, config_path: str):
        try:
            self._config_handler = ConfigHandler(config_path)
        except ConfigurationException as exc:
            raise IncorrectConfigFileError('The configuration file contains mistakes') from exc

        self._worker_name = self._config_handler.get_worker_name()
        self._worker_address = self._config_handler.get_worker_address()
        self._master_address = self._config_handler.get_master_address()
        self._timeout = self._config_handler.get_reconnect_timeout()
        self._frequency = self._config_handler.get_reconnect_frequency()
        self._authentification_token = self._config_handler.get_authentification_token()
        self.mountpoints = self._config_handler.get_mountpoints()

    def create_objects(self, ):
        """Initialize all the Objects according to the attributes read in configfile.
        
        :raises StorageNotMountedError: If a Storage is not mounted at its given mountpath.
        """
        # first we create MsgOut:
        self._msg_out = Out(self._master_address, self._authentification_token, self._timeout,
                            self._frequency)
        self._worker = Worker(self._worker_name, self._msg_out, self.mountpoints)

    def register_to_master(self):
        aliases = []
        for key, storage in self._storages.items():
            aliases.append(key)
        # the order is important!
        self._msg_out.register(self._master_address, self._authentification_token,
                               self._worker_name,
                               self._worker_address, self.mountpoints, self._worker.status)
        self._msg_in = MsgIn(self._authentification_token, self._worker_address, self._msg_out,
                             self._worker)

    def run_app(self):
        app = Flask(__name__)
        _dummy, _host, _port = self._worker_address.split(':')
        app.config['DEBUG'] = False
        app.config['MSGIN'] = self._msg_in
        app.config['token'] = self._authentification_token
        app.register_blueprint(api)
        app.before_request(unmunge_request)
        app.after_request(munge_response)
        app.run(host=_host.strip('/'), port=int(_port))



