#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify
from views.CmdView.print_parser import parse_to_list
import requests


class Storages(Command):
    def __init__(self, obj, args):
        super(Storages, self).__init__(obj)
        self.args = args

    def execute(self, token, username, ):
        args = self.args
        cookies = dict(username=username,token=token)
        params = dict()

        if args.command == 'list':
            user = args.user if args.user else username

            if args.storage and args.all:
                url = os.path.join(Tokenify.get_url(), 'storages', str(args.storage))
                params = {'dirs': 'True'}

            elif args.storage:
                url = os.path.join(Tokenify.get_url(), 'users', user, 'storages',
                                   str(args.storage))

            elif args.all:
                url = os.path.join(Tokenify.get_url(), 'storages/')
                params = {'dirs': 'True'}

            elif args.user or args.dirs:
                url = os.path.join(Tokenify.get_url(), 'users', user, 'storages/')

            else:
                # "dmd storage list" prints list of storages w/ info about them
                url = os.path.join(Tokenify.get_url(), 'storages/')
            r, text = self.send_request('get', url, cookies=cookies, params=params)

        elif args.command == 'set':
            url = os.path.join(Tokenify.get_url(), 'storages/', args.alias)
            p = re.compile('([^=])+=([^=])+').match(args.keyvalue)
            if not p:
                print('Bad syntax, can\'t process request')
                return
            key, value = args.keyvalue.split('=')
            body = dict(key=key, value=value)
            r, text = self.send_request('patch', url, cookies=cookies, json=body)
        else:
            print('Invalid command.')
            return

        if r.status_code == 200 or r.status_code == 204:
            print(parse_to_list(text))
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
