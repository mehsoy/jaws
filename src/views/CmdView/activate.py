#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify


class Activate(Command):
    def __init__(self, object, obj, id = None):
        super(Activate, self).__init__(obj)
        self.object = object
        self.id = id

    def execute(self, token, username):
        body = {'status': 'ACTIVE'}
        cookies = dict(username=username, token=token)

        if self.object not in ['worker', 'master']:
            print("Object " + self.object + " not known")
            return

        elif self.object == 'worker':
            self.check_id(self.id)
            url = os.path.join(Tokenify.get_url(), 'workers', str(self.id))

        elif self.object == 'master':
            url = os.path.join(Tokenify.get_url(), 'master')

        r, text = self.send_request('patch', url, cookies=cookies, json=body)

        if r.status_code == 200 or r.status_code == 204:
            print(self.object + ' ' + str(self.id) + ' activated!')
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)

    def check_id(self,id):
        if id is None:
            print("Id for Storage or Worker needed")
            exit(0)
