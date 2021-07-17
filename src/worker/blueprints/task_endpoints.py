""".. module: task_endpoints"""
import json
import sys

from flask import request, jsonify, abort, current_app, make_response, g
from flask_restplus import Namespace, Resource

from worker.blueprints.schema import binary_status_schema, job_schema


ns = Namespace('task')


@ns.route('/')
class TaskItem(Resource):

    def patch(self):
        """PATCH /task
        
        Change the status of the task, that this worker is currently working on.

        **JSON Body Parameters:**

        - **status** - Can currently only be set to ``ACTIVE`` to
          resume a paused task.

        """
        req = binary_status_schema(g.payload)
        if req.get('status') == 'ACTIVE':
            answer = current_app.config['MSGIN'].resume_paused_task()
        else:
            answer = ''
        return jsonify(answer)

    def delete(self):
        """ DELETE /task

        Cancels the currently executed task.

        """
        answer = current_app.config['MSGIN'].cancel_task()
        return jsonify(answer)
    
    def post(self):
        """POST /task

        Creates a new job request.

        **JSON Body Parameters:**

        - **source_alias**(str) - the directory, which is to be transfered
        - **source_path**(str)
        - **target_alias**(str) - the directory files  will be moved to
        - **job_id**(str) - the id of this job
        - **for_user**(str) - the user for whom the directory is moved. [optional][restricted to ``Administrator``]


        """
        req = job_schema(g.payload)
        answer = current_app.config['MSGIN'].assign_task(**req)
        return make_response(jsonify(answer), 200)

