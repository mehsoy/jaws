import os

from views.CmdView.command import Command
from views.CmdView.tokenify import Tokenify

class ShareInfo(Command):
    def __init__(self, obj, full_name):
        super(ShareInfo, self).__init__(obj)
        self.full_name = full_name

    def execute(self, token, username):
        cookies = dict(username=username, token=token)
        url = os.path.join(Tokenify.get_url(), 'workspaces', self.full_name, 'access')

        r, text = self.send_request('get', url, cookies=cookies)

        if 200 <= r.status_code < 300:
            print(text)
        else:
            print(str(r.status_code) + '---- HTTP GET ERROR')
            print(text)

