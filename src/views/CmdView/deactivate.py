#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from views.CmdView.tokenify import Tokenify
from views.CmdView.command import Command


class Deactivate(Command):
    def __init__(self, object, obj, id=None):
        super(Deactivate, self).__init__(obj)
        self.id = id
        self.object = object

    def execute(self, token, username):
        body = {'status': 'DEACTIVATED'}
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
            print(self.object + ' ' + str(self.id) + ' deactivated!')
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)

    def check_id(self,id):
        if id is None:
            print("Id for Storage or Worker needed")
            exit(0)
