#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from views.CmdView.tokenify import Tokenify
from views.CmdView.command import Command


class Move(Command):
    def __init__(self, workspace, target, obj, a=False, b=False, e=False, user=None):
        super(Move, self).__init__(obj)
        self.workspace = workspace
        self.target = target
        self.a = a
        self.b = b
        self.e = e
        self.user = user

    def execute(self, token, username):
        url = os.path.join(Tokenify.get_url(), 'jobs/')
        cookies = dict(username=username, token=token)
        data = {'workspace': self.workspace,
                'target': self.target,
                'a': self.a,
                'b': self.b,
                'e': self.e,
                'for_user': self.user
                }

        r, text = self.send_request('post', url, cookies=cookies, json=data)

        if r.status_code == 200 or r.status_code == 204:
            print('The job\'s identifier is ' + str(text))
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
