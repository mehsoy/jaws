#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify


class Rights(Command):
    def __init__(self, role, user, obj=None):
        super(Rights, self).__init__(obj)
        self.role = role
        self.user = user

    def execute(self, token, username):
        body = {'role': self.role}
        url = os.path.join(Tokenify.get_url(), 'users', str(self.user))
        cookies = dict(username=username, token=token)

        r, text = self.send_request('patch', url, cookies=cookies, json=body)

        if r.status_code == 200 or r.status_code == 204:
            print(self.user + ' set to ' + self.role + ' !')
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
