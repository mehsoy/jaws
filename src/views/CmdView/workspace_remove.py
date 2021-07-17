#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from views.CmdView.tokenify import Tokenify
from views.CmdView.command import Command


class WorkspaceRemove(Command):
    def __init__(self, workspace, target, obj, a=False, b=False, e=False, user=None):
        super(WorkspaceRemove, self).__init__(obj)
        self.workspace = workspace
        self.target = target
        self.a = a
        self.b = b
        self.e = e
        self.user = user

    def execute(self, token, username):
        url = os.path.join(Tokenify.get_url(), 'workspace/')
        cookies = dict(username=username, token=token)
        query_string = '?name=' + self.workspace
        url = os.path.join(Tokenify.get_url(), 'workspaces/', query_string)
        body = dict(action='remove')

        #r, text = self.send_request('put', url, cookies=cookies, json=body)
        r, text = self.send_request('put', url, cookies=cookies, json=body)

        if r.status_code == 200 or r.status_code == 204:
            print('Workspace ' + text[0] + ' successfully removed. Status: ' + text[1])
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
