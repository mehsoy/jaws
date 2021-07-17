import os

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify


class Share(Command):
    def __init__(self, obj, tag_type, name, instruction, full_name):
        super(Share, self).__init__(obj)
        self.tag_type = tag_type
        self.name = name
        self.instruction = instruction
        self.full_name = full_name

    def execute(self, token, username):
        cookies = dict(username=username, token=token)
        url = os.path.join(Tokenify.get_url(), 'workspaces', self.full_name, 'access')
        data = { 
            'tag_type': self.tag_type,
            'name': self.name,
            'instruction': self.instruction
        }

        r, text = self.send_request('patch', url, cookies=cookies, json=data)

        if 200 <= r.status_code < 300:
            print(text)
        else:
            print(str(r.status_code) + '---- HTTP PATCH ERROR')
            print(text)

