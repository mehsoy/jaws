#!/usr/bin/python
#-*- coding: utf-8 -*-

import os

from helpers import munge_response, unmunge_request
from .config_handler import ConfigHandler
from flask import Flask

from .blueprints.api import blueprint as api
from .blueprints.errors import blueprint as errors
from .master import Master

class MasterInitializer:
    def __init__(self, config_path):
        if (not os.path.exists(config_path)):
            raise IncorrectConfigFileError("No config was found at " + config_path)
        self.create_objects(ConfigHandler(config_path))    
        
    def create_objects(self, handler):
        app = Flask(__name__)
        _, _host, _port= handler.get_address().split(':')
        app.config['DEBUG'] = False
        app.config['token'] = handler.get_token()
        app.before_request(unmunge_request)
        app.after_request(munge_response)
        app.register_blueprint(api)
        app.register_blueprint(errors)
        app.run(host=_host.strip('/'), port=int(_port))
        # pot. 2nd arg:
        # handler.get_active_on_start()
        master = Master.get_master(handler.get_token())

