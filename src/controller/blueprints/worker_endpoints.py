""".. module:: worker_endpoints """
import json

from flask import request, abort, jsonify, current_app, make_response, g
from flask_restplus import Resource, Namespace

from controller.blueprints import valid_roles
from controller.schema import binary_status_schema


ns = Namespace('workers')


@ns.route('/')
class WorkerCollection(Resource):

    @valid_roles(['Administrator'])
    def get(self):
        """GET /workers
        
        :return: list of all workers and their status

        """
        workers = current_app.config['APPLICATION'].get_workers()
        return jsonify(workers)


@ns.route('/<int:identifier>')
class WorkerItem(Resource):

    @valid_roles(['Administrator'])
    def patch(self, identifier):
        """PATCH /workers/<identifier>

        Changes the status of this worker.

        **JSON Body Parameters:**
        
        - **status** - can be set to ``ACTIVE`` or ``DEACTIVATED``

        """

        data = binary_status_schema(g.payload)
        if data.get('status') == 'ACTIVE':
            current_app.config['APPLICATION'].enable_worker(identifier)
        elif data.get('status') == 'DEACTIVATED':
            current_app.config['APPLICATION'].disable_worker(identifier)
        else:
            abort(400)
        return make_response(jsonify(''), 204)

