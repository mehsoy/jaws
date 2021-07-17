""".. module:: worker_endpoints"""
import json

from flask import abort, jsonify, request, current_app, g
from flask_restplus import Namespace, Resource

from worker.blueprints.schema import binary_status_schema


ns = Namespace('workers')


@ns.route('/')
class WorkerItem(Resource):

    def patch(self):
        """PATCH /workers

        Change the status of this worker.

        **JSON Body Parameter:**

        - **status**(str) - Can be either ``ACTIVE`` or ``DEACTIVATED`` 

        """
        req = binary_status_schema(g.payload)
        if req.get('status') == 'DEACTIVATED':
            current_app.config['MSGIN'].deactivate_worker()
        elif req.get('status') == 'ACTIVE':
            current_app.config['MSGIN'].activate_worker()
        else:
            abort(422)
        return jsonify('')

    def get(self):
        answer = {
                'status': current_app.config['MSGIN'].get_status(),
                'id': current_app.config['MSGIN'].get_worker_name()
                }
        return jsonify(answer)
        

