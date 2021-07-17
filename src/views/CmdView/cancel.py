#!/usr/bin/python
# -*- coding: utf-8 -*-
from views.CmdView.command import Command
from  views.CmdView.tokenify import Tokenify
import requests
import os

class Cancel(Command):
    def __init__(self, id, obj):
        super(Cancel, self).__init__(obj)
        self.id = id

    def execute(self, token, username):
        url = os.path.join(Tokenify.get_url(), 'jobs/',str(self.id))
        cookies = dict(username=username, token=token)

        r, text = self.send_request('delete', url, cookies=cookies)

        if r.status_code == 200 or r.status_code == 204:
            print("Job canceled.")
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
