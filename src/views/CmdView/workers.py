#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify
from views.CmdView.print_parser import parse_to_list


class Workers(Command):
    def __init__(self, obj):
        super(Workers, self).__init__(obj)

    def execute(self, token, username):
        url = os.path.join(Tokenify.get_url(), 'workers/')
        cookies = dict(username=username, token=token)

        r, text = self.send_request('get', url, cookies=cookies)

        if r.status_code == 200 or r.status_code == 204:
            print("----- Worker Overview -----")
            print(parse_to_list(text))
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
