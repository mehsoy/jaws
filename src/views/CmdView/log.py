#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from views.CmdView.tokenify import Tokenify
from views.CmdView.command import Command
from views.CmdView.print_parser import parse_to_list


class Log(Command):
    def __init__(self, days, obj, user=None):
        super(Log, self).__init__(obj)
        self.days = days
        self.user = user

    def execute(self, token, username):
        parameters = {'status': 'DONE', 'days': str(self.days)}
        cookies = dict(username=username, token=token)

        if self.user is None:
            url = os.path.join(Tokenify.get_url(), 'users', username, 'jobs/')
        else:
            url = os.path.join(Tokenify.get_url(), 'users', str(self.user), 'jobs/')

        r, text = self.send_request('get', url, cookies=cookies, params=parameters)

        if r.status_code == 200 or r.status_code == 204:
            print("----- Log Overview -----")
            print(parse_to_list(text), end='')
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)

