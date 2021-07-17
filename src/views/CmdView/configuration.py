#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from views.CmdView.tokenify import Tokenify
from views.CmdView.command import Command
from views.CmdView.print_parser import parse_to_list
import pprint

#TODO add other config endpoints and check for pretty print

class Configuration(Command):
    def __init__(self, configfile, obj):
        super(Configuration, self).__init__(obj)
        self.configfile = configfile


    def execute(self, token, username):
        url = os.path.join(Tokenify.get_url(), 'configuration/' + self.configfile)
        cookies = dict(username=username, token=token)

        r, text = self.send_request('get', url, cookies=cookies)

        if r.status_code == 200 or r.status_code == 204:
            print("----- Config Overview of " + self.configfile + " -----")
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(text)
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)

