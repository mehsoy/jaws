""".. module:: target_endpoints """
import json
from json import dumps, loads

from flask import request, jsonify, abort, current_app, make_response, g
from flask_restplus import Resource, Namespace

from application.handlers.config_handler import ConfigHandler, get_ini_configuration, get_storages_configuration, get_controller_configuration
from . import valid_roles
from ..schema import binary_status_schema, patch_access_schema

from helpers import get_conf_directory
from configparser import ConfigParser
ns = Namespace('configuration')



@ns.route('/')
class ConfigurationCollection(Resource):
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
class ConfigurationMaster(Resource):
    """
    Returns Configuration
    """
    @valid_roles()
    def get(self,identifier):
        controller_configuration = get_ini_configuration(identifier)
        return jsonify(controller_configuration)


# @ns.route('/controller')
# class ConfigurationMaster(Resource):
#     """
#         Returns configuration from Controller
#     """
#
#     @valid_roles()
#     def get(self,):
#         controller_configuration = get_controller_configuration()
#         return jsonify(controller_configuration)
#
# @ns.route('/storages')
# class ConfigurationMaster(Resource):
#     """
#         Returns configuration of available storages
#     """
#
#     @valid_roles()
#     def get(self,):
#         storages = get_storages_configuration()
#         return jsonify(storages)

