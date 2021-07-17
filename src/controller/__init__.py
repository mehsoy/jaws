from flask import request, g, Response
from json import loads, dumps
from pymunge import MungeContext
from pwd import getpwuid

from application.handlers.config_handler import ConfigHandler


def extract_action_log():
    if not g.munge: return
    if not g.payload.get('action_log'):
        print('WARNING: ACTION LOG WASN\'T GENERATED')
        return
    log_entry = g.payload.pop('action_log')
    with open(ConfigHandler().action_log_path, 'a+') as f:
        s = ','.join([g.username, g.pop('source_ip'), log_entry]) + '\n'
        f.write(s)

# Controller needs special (un-)munge methods unlike the other packages who use the func
# from ``helpers``. This is because the controller needs to be able to handle munged AND un-
# munged requests at the same time while the other packages don't.

def unmunge_request():

    body = request.json
    g.munge = True if body is not None and body.get('munge_cred') else False
    if not g.munge:
        g.payload = body
        return

    cred = body['munge_cred'].encode('utf-8')
    with MungeContext() as ctx:
        payload, uid, gid = ctx.decode(cred)
        g.source_ip = ctx.addr4
    g.username = getpwuid(uid).pw_name
    g.payload = loads(payload.decode('utf-8'))


def munge_response(response: Response):
    if g.munge:
        body = response.json
        payload = dumps(body).encode('utf-8')
        with MungeContext() as ctx:
            cred = ctx.encode(payload).decode('utf-8')
        json = dumps(dict(munge_cred=cred))
        response.data = json
        return response
    else:
        return response


