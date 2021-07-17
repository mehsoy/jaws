#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify
from views.CmdView.print_parser import parse_to_list


class Job(Command):
    def __init__(self, obj, id):
        super(Job, self).__init__(obj)
        self.id = id

    def execute(self, token, username):
        url = os.path.join(Tokenify.get_url(), 'jobs/', str(self.id))
        cookies = dict(username=username, token=token)

        r, text = self.send_request('get', url, cookies=cookies)

        if r.status_code == 200 or r.status_code == 204:
            print(parse_to_list(text), end='')
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
