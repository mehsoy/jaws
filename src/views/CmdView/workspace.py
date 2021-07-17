#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re

from json import loads

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify
from views.CmdView.print_parser import parse_to_list


class Workspace(Command):
    def __init__(self, obj, args):
        super(Workspace, self).__init__(obj)
        self.args = args

    def execute(self, token, username):
        args = self.args
        cookies = dict(username=username, token=token)

        if args.command == 'list':
            url = os.path.join(Tokenify.get_url(), 'workspaces/')
            if not args.all: url += '?for_user=' + cookies['username']
            r, text = self.send_request('get', url, cookies=cookies)

        elif args.command == 'create':
            url = os.path.join(Tokenify.get_url(), 'workspaces/')
            body = dict(name=args.label)
            # if args.storage: body['storage'] = args.storage
            r, text = self.send_request('post', url, cookies=cookies, json=body)

        elif args.command == 'extend':
            query_string = '?name=' + args.full_name
            url = os.path.join(Tokenify.get_url(), 'workspaces/', query_string)
            body=dict(action='extend')
            r, text = self.send_request('put', url, cookies=cookies, json=body)

        elif args.command == 'remove':
            query_string = '?name=' + args.full_name
            url = os.path.join(Tokenify.get_url(), 'workspaces/', query_string)
            body=dict(action='remove')
            r, text = self.send_request('put', url, cookies=cookies, json=body)

        elif args.command == 'set':
            url = os.path.join(Tokenify.get_url(), 'workspaces/', args.full_name)
            p = re.compile('([^=])+=([^=])+').match(args.keyvalue)
            if not p:
                print('Bad syntax, can\'t process request')
                return
            key, value = args.keyvalue.split('=')
            body= dict(key=key, value=value)
            r, text = self.send_request('patch', url, cookies=cookies, json=body)
        else:
            print('Invalid command.')
            return

        if r.status_code == 200 or r.status_code == 204:
            if args.command == 'list':
                print("Workspace Overview:")
                print(parse_to_list(text))
            if args.command == 'create':
                print('Created new Workspace ' + text)
            elif args.command == 'extend':
                print('Workspace ' + text[0] + ' successfully extended. Time Remaining: ' + text[1])
            elif args.command == 'remove':
                print('Workspace ' + text[0] + ' successfully removed. Status: ' + text[1])
        else:
            print(str(r.status_code) + "---- HTTP REQUEST GET'S ERROR")
            print(text)
