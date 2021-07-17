import spwd

import crypt
import json
from json import dumps, loads
import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, make_response, abort
from flask import current_app
from werkzeug.wrappers import Response

from controller.blueprints import templated, valid_roles
from views.CmdView.cancel import Cancel
from views.CmdView.move import Move
from views.CmdView.workspace_remove import WorkspaceRemove


ns = Blueprint('ns', __name__, url_prefix='/web', static_folder='../static')


@ns.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and checklogin(request.form['username'], request.form['psw']):

        username = request.form['username']
        current_app.config['APPLICATION'].ensure_existance(username)
        token = current_app.config['APPLICATION'].get_credentials_by_user(username)['token']
        role = current_app.config['APPLICATION'].get_user_type(username)

        if role == 'Administrator':
            response = make_response(redirect(url_for('ns.admin')))
            Response.set_cookie(response, key="username", value=username)
            Response.set_cookie(response, key="token", value=token)
            return response
        elif role == 'User':
            response = make_response(redirect(url_for('ns.user')))
            Response.set_cookie(response, key="username", value=username)
            Response.set_cookie(response, key="token", value=token)
            return response
        else:
            return render_template('login.html')

    return render_template('login.html')


# If route is changed, see web_app_event namespaces
@ns.route('/admin/dashboard', methods=['GET'])
@valid_roles(['Administrator'])
@templated('admin_dashboard.html')
def admin():
    url_queue = os.path.join('http://', current_app.config['SERVER_ADDRESS'], 'api', 'jobs/')
    cookies = dict(username=request.cookies.get('username'), token=request.cookies.get('token'))
    parameters_queue = {'status': 'ENQUEUED'}
    queue_jobs = requests.get(url_queue, cookies=cookies, params=parameters_queue)

    url_active = os.path.join('http://', current_app.config['SERVER_ADDRESS'], 'api', 'users',
                              request.cookies.get('username'), 'jobs/')
    parameters_active = {'status': 'ACTIVE'}
    active_jobs = requests.get(url_active, cookies=cookies, params=parameters_active)

    url_worker = os.path.join('http://', current_app.config['SERVER_ADDRESS'], 'api', 'workers/')
    workers = requests.get(url_worker, cookies=cookies)

    url_workspaces = os.path.join('http://', current_app.config['SERVER_ADDRESS'],
                                     'api', 'workspaces/')
    workspaces = requests.get(url_workspaces, cookies=cookies)

    return dict(jobs=json.loads(active_jobs.text),
                jobs_queue=json.loads(queue_jobs.text),
                workers=json.loads(workers.text),
                workspaces=json.loads(workspaces.text))


@ns.route('/dashboard', methods=['GET', 'POST'])
@templated('user.html')
@valid_roles()
def user():
    cookies = dict(username=request.cookies.get('username'), token=request.cookies.get('token'))

    if request.method == 'GET':

        url_active = os.path.join('http://', current_app.config['SERVER_ADDRESS'], 'api', 'users',
                                  request.cookies.get('username'), 'jobs/')
        parameters_active = {'status': 'ACTIVE'}
        active_jobs = requests.get(url_active, cookies=cookies, params=parameters_active)

        url_storage_names = os.path.join('http://', current_app.config['SERVER_ADDRESS'],
                                         'api', 'storages')
        parameters = {'dirs': 'False'}
        storage_names = requests.get(url_storage_names, cookies=cookies, params=parameters)
        storage_names = [s['alias'] for s in loads(storage_names.text)]

        return dict(jobs=json.loads(active_jobs.text),
                    storage_names=storage_names)

    elif request.method == 'POST' and 'to_delete' not in request.form:
        # Since html forms don't support HTTP DELETE requests, deletion requests
        # are recognized by the `to_delete` form field.
        workspace = request.form['workspace']
        target = request.form['target']
        Move(workspace=workspace, target=target, obj=None).execute(**cookies)
        return redirect(url_for('ns.user'))

    elif 'to_delete' in request.form:
        job_id = request.form['to_delete']
        Cancel(id=job_id, obj=None).execute(**cookies)
        return redirect(url_for('ns.user'))


@ns.route('/storages/')
@templated('storage_overview.html')
@valid_roles()
def storage_overview():
    cookies = dict(username=request.cookies.get('username'), token=request.cookies.get('token'))
    url_storages = os.path.join('http://', current_app.config['SERVER_ADDRESS'],
                                     'api', 'storages/')
    storages = requests.get(url_storages, cookies=cookies)
    return dict(storages=json.loads(storages.text))

@ns.route('/jobs/past', methods=['GET'])
@templated('past_jobs.html')
@valid_roles()
def past_jobs():
    cookies = dict(username=request.cookies.get('username'), token=request.cookies.get('token'))
    url_finished_jobs = os.path.join('http://', current_app.config['SERVER_ADDRESS'],
                                     'api', 'users', request.cookies.get('username'), 'jobs/')
    parameters = {'status': 'DONE', 'days': 30}
    finished_jobs = requests.get(url_finished_jobs, cookies=cookies, params=parameters)
    return dict(finished_jobs=json.loads(finished_jobs.text))


@ns.route('/workspaces', methods=['GET','POST'])
@templated('workspaces.html')
@valid_roles()
def workspaces():
    cookies = dict(username=request.cookies.get('username'), token=request.cookies.get('token'))

    if request.method == 'GET':
        url_workspaces = os.path.join('http://', current_app.config['SERVER_ADDRESS'],
                                         'api', 'workspaces', f"?for_user={cookies['username']}")
        workspaces = requests.get(url_workspaces, cookies=cookies)
        return dict(workspaces=json.loads(workspaces.text))
    elif request.method == 'POST':
        workspace_del = request.form['workspace_delete']
        WorkspaceRemove(workspace=workspace_del, target="blub2", obj=None).execute(**cookies)
        return render_template('workspaces.html')


@ns.route('/wip')
def wip():
    return render_template('wip.html')


@ns.route('/logout')
def logout():
    response = make_response(redirect(url_for('ns.login')))
    Response.set_cookie(response, key="username", expires=0)
    Response.set_cookie(response, key="token", expires=0)

    return response


def checklogin(user, password) -> bool:
    """Tries to authenticate a user.
    Returns True if the authentication succeeds, else the reason
    (string) is returned."""
    try:
        return True
        enc_pwd = spwd.getspnam(user)[1]
        print(enc_pwd)
        if enc_pwd in ["NP", "!", "", None]:
            # TODO should this return true or false?
            return "user '%s' has no password set" % user
        if enc_pwd in ["LK", "*"]:
            return False
        if enc_pwd == "!!":
            return False
        # Encryption happens here, the hash is stripped from the
        # enc_pwd and the algorithm id and salt are used to encrypt
        # the password.
        if crypt.crypt(password, enc_pwd) == enc_pwd:
            return True
        else:
            return False
    except KeyError:
        return False
