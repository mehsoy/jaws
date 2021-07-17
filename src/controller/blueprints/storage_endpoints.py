""".. module:: storage_endpoints """
import json
from json import dumps, loads

from flask import request, jsonify, abort, current_app, make_response, g
from flask_restplus import Resource, Namespace

from . import valid_roles
from ..schema import binary_status_schema, patch_access_schema


ns = Namespace('storages')


@ns.route('/')
class StorageCollection(Resource):
    """Enables operations on the aggregate of all storages."""

    @valid_roles()
    def get(self):
        """Lists all storages.

        **Query String Parameters:**

        - **dirs**(boolean) - Set to ``true``, if you want all directories of a storage
          to be shown. Needs Administrator privilege to enable this feature. Otherwise details
          for every storage are returned.
          [optional]

        :return: A dict of all storages and potentially its corresponding  directories
        :rtype: String
        """
        role = current_app.config['APPLICATION'].get_user_type(g.username)
        dirs = request.args.get('dirs')
        data = dict(user=g.username)
        if dirs == 'True' and role == 'Administrator':
            r = current_app.config['APPLICATION'].get_directory_list(**data)
        elif dirs is None or dirs == 'False':
            r = current_app.config['APPLICATION'].get_storages()
        else:
            abort(401)
        return jsonify(r)


@ns.route('/<string:identifier>')
class StorageItem(Resource):
    """Enables operations on single storage."""

    @valid_roles()
    def get(self, identifier):
        """GET /storages/<identifier>
        
        List all directories in this storage.

        :param id: The unique identifier of the storage
        :type id: String
        :return: A list of directories in this storage
        """
        args = dict(storage=identifier, user=g.username)
        resp = current_app.config['APPLICATION'].get_directory_list(**args)
        return jsonify(resp)

    @valid_roles(['Administrator'])
    def patch(self, identifier):
        key = g.payload['key']
        value = g.payload['value']
        current_app.config['APPLICATION'].set_in_database('storages', key, value, identifier, g.username)
        return '', 204