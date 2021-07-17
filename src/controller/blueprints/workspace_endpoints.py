""".. module:: target_endpoints """
import json
from json import dumps, loads

from flask import request, jsonify, abort, current_app, make_response, g
from flask_restplus import Resource, Namespace

from application.handlers.config_handler import ConfigHandler
from . import valid_roles
from ..schema import binary_status_schema, patch_access_schema

ns = Namespace('workspaces')


@ns.route('/')
class WorkspaceCollection(Resource):

    @valid_roles()
    def get(self):
        for_user = request.args.get('for_user', default=None, type=str)
        user_type = current_app.config['APPLICATION'].get_user_type(g.username)
        if g.username != for_user and user_type != 'Administrator':
            abort(401)
        r = current_app.config['APPLICATION'].get_workspaces(for_user)
        return jsonify(r)

    @valid_roles()
    def put(self):
        name = request.args.get('name')
        body = g.payload
        if body['action'] == 'extend':
            user_type = current_app.config['APPLICATION'].get_user_type(g.username, as_string=False)
            r = current_app.config['APPLICATION'].extend_workspace(g.username, user_type, name)
        elif body['action'] == 'remove':
            user_type = current_app.config['APPLICATION'].get_user_type(g.username, as_string=False)
            r = current_app.config['APPLICATION'].remove_workspace(g.username, user_type, name)
        else: abort(400)
        return jsonify(r)

    @valid_roles()
    def post(self):
        ws_label = g.payload['name']
        storage_alias = g.payload.get('storage')
        r = current_app.config['APPLICATION'].create_workspace(
            username=g.username, ws_label=ws_label, storage_alias=storage_alias)
        return jsonify(r)


@ns.route('/<string:full_name>')
class WorkspaceItem(Resource):

    @valid_roles()
    def patch(self, full_name):
        key = g.payload['key']
        value = g.payload['value']
        current_app.config['APPLICATION'].set_in_database('workspaces', key, value, full_name, g.username)
        return '', 204

@ns.route('/<string:full_name>/access')
class WorkspaceItemAccess(Resource):

    @valid_roles()
    def get(self, full_name):
        username, label, counter = ConfigHandler().disassemble_workspace_full_name(full_name)
        perms = current_app.config['APPLICATION'].get_workspace_permission(username, label, counter)
        return jsonify(perms)

    @valid_roles()
    def patch(self, full_name):
        '''Use this to modify the files's acl'''
        pa = patch_access_schema(g.payload)
        if not is_plausible_entry(pa['tag_type'], pa['name']):
            raise SyntaxError('Bad Request.')

        role = current_app.config['APPLICATION'].get_user_type(g.username)

        # not specifying caller indicates full authority and access rights
        caller = (None if role == 'Administrator' else g.username)
        username, label, counter = ConfigHandler().disassemble_workspace_full_name(full_name)

        req = {
            'username': username,
            'label': label,
            'counter': counter,
            'caller': caller,
            'tag_type': pa['tag_type'],
            'name': pa['name'],
            'instruction': pa['instruction'],
        }
        current_app.config['APPLICATION'].put_workspace_permission(**req)
        return '', 204

def is_plausible_entry(tag_type, name):
    if (tag_type != 'other') and name or tag_type == 'other' and not name:
        return True
    else:
        return False



