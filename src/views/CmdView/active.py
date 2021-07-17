#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import requests

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify
from views.CmdView.print_parser import parse_to_list


class Active(Command):
    def __init__(self, obj, user=None, all=False):
        super(Active, self).__init__(obj)
        self.user = user
        self.all = all

    def execute(self, token, username):
        cookies = dict(username=username, token=token)
        parameters = {'status': ['ACTIVE', 'QUEUED']}
        if self.user is None and not self.all:
            url = os.path.join(Tokenify.get_url(), 'users', str(username), 'jobs/')
        elif self.all:
            url = os.path.join(Tokenify.get_url(), 'jobs/')
        else:
            url = os.path.join(Tokenify.get_url(), 'users', self.user, 'jobs/')

        r, text = self.send_request('get', url, cookies=cookies, params=parameters)

        if r.status_code == 200 or r.status_code == 204:
            print("----- Active Jobs -----")
            print(parse_to_list(text))
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
