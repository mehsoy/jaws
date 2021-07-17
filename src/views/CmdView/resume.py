#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify
import requests


class Resume(Command):
    def __init__(self, id, obj):
        super(Resume, self).__init__(obj)
        self.id = id

    def execute(self, token, username):
        body = {'status': 'ACTIVE'}
        url = os.path.join(Tokenify.get_url(), 'jobs', str(self.id))
        cookies = dict(username=username, token=token)

        r, text = self.send_request('patch', url, cookies=cookies, json=body)

        if r.status_code == 200 or r.status_code == 204:

            print(text)
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
