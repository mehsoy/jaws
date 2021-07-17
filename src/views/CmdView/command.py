#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import request, g, Response
import requests
from json import dumps, loads
from pymunge import MungeContext

from helpers import unmunge, use_munge


class Command(object):
    def __init__(self, obj):
        """
        Given constructor of the command with his parameter
        :param obj:
        """
        self.current_command = None

    def send_request(self, *args, **kwargs) -> (Response, str):
        if not kwargs.get('json'):
            kwargs['json'] = dict()
        if use_munge():
            if self.current_command: kwargs['json']['action_log'] = self.current_command
            with MungeContext() as ctx:
                cred = ctx.encode(dumps(kwargs['json']).encode('utf-8')).decode('utf-8')
            kwargs['json'] = dict(munge_cred=cred)
            r = requests.request(*args, **kwargs)
            if r.text:
                return r, loads(unmunge(r.text))
            else:
                return r, r.text
        else:
            r = requests.request(*args, **kwargs)
            return r, loads(r.text)

    def execute(self, token, username):
        """
        Executes the command of the command pattern and launches the HTTP request and prints the given
        Result
        :param token:Token of the specific User
        :param username: Username of the specific User
        :return: None
        """
        print("Unknown Command - please insert valid Command")
        return
