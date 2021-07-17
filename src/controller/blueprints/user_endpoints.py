""".. module:: user_endpoints """
import json

from flask import request, jsonify, abort, current_app, make_response, g
from flask_restplus import Namespace, Resource

from . import valid_roles
from ..schema import role_schema


ns = Namespace('users')


@ns.route('/<string:identifier>')
class UserItem(Resource):

    @valid_roles(['Administrator'])
    def get(self, identifier):
        try:
            role = current_app.config['APPLICATION'].verify_user({ 'user': identifier })
            return role
        except Exception as e:
            return make_response(str(e), 500)

    @valid_roles(['Administrator'])
    def patch(self, identifier):
        """PATCH /users/<identifier>

        **JSON Request Parameters:**

        - **role** - the role of a user

        """
        args = role_schema(g.payload)
        args['user'] = identifier
        current_app.config['APPLICATION'].set_rights(**args)
        return make_response(jsonify(''), 204)



@ns.route('/<string:identifier>/jobs/')
class UserJobs(Resource):

    @valid_roles()
    def get(self, identifier):
        """ GET /users/<identifier>/jobs

        Returns all jobs of this user.
        
        ** Query String Parameters: **

        - **status** - set to ``ACTIVE`` to return active jobs
          or ``DONE`` to return finished jobs. Defaults to ``DONE``. [optional]
        - **days**(int) - in case ``status`` equals ``DONE`` this determines the
          timeframe, from which entries are displayed. Defaults to ``12``. [optional]
        
        :return: a list of job logs.

        """
        username = request.cookies.get('username')
        status = request.args.getlist(key='status')
        if not status: status = ['DONE']
        days = request.args.get('days', default=12, type=int)
        if not 'DONE' in status: days = None

        app_request = {
                'user': username,
                'for_user': identifier,
                'statuses': status,
                'days': days,
                }
        r = current_app.config['APPLICATION'].get_jobs(**app_request)
        return jsonify(r)


@ns.route('/<string:identifier>/storages/')
class UserStorageCollection(Resource):

    @valid_roles()
    def get(self, identifier):
        """GET /users/<identifier>/storages

        :return: a list of storages, with their respective
        directories of this user.
        
        """
        data = dict(user=g.username, for_user=identifier)
        r = current_app.config['APPLICATION'].get_directory_list(**data)
        return jsonify(r)

@ns.route('/<string:user>/storages/<storage_alias>')
class UserStorageItem(Resource):

    @valid_roles()
    def get(self, user, storage_alias):
        args = dict(user=g.username, for_user=user, storage=storage_alias)
        response = current_app.config['APPLICATION'].get_directory_list(**args)
        return jsonify(response)









