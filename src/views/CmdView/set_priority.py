#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from views.CmdView.tokenify import Tokenify
from views.CmdView.command import Command


class SetPriority(Command):
    def __init__(self, obj, priority, id):
        super(SetPriority, self).__init__(obj)
        self.priority = priority
        self.id = id

    def execute(self, token, username):
        body = {'priority': self.priority}
        url = os.path.join(Tokenify.get_url(), 'jobs', str(self.id))
        cookies = dict(username=username, token=token)

        r, text = self.send_request('patch', url, cookies=cookies, json=body)

        if r.status_code == 200 or r.status_code == 204:
            print(text)
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
