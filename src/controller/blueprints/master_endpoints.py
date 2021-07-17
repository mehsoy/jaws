""".. module:: master_endpoints """
import json

from flask import request, abort, jsonify, current_app, make_response, g
from flask_restplus import Resource, Namespace

from . import valid_roles
from ..schema import binary_status_schema


ns = Namespace('master')


@ns.route('')
class MasterItem(Resource):

    @valid_roles(['Administrator'])
    def patch(self, identifier):
        """Change status of the Master. 
        
        **JSON Body Parameters:**
        
        - **status** - can be either ``ACTIVE`` or ``DEACTIVATED``.

        :raises 422: if the value of status is not valid.

        """
        data = binary_status_schema(g.payload)
        if data.get('status') == 'ACTIVE':
            current_app.config['APPLICATION'].enable_master(json.dumps(data))
        elif data.get('status') == 'DEACTIVATED':
            current_app.config['APPLICATION'].disable_master(json.dumps(data))
        else:
            abort(422)
        return make_response(jsonify(''), 204)

