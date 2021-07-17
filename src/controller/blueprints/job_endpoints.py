""".. module:: job_endpoints """
import json
from json import dumps

from flask import request, abort, jsonify, current_app, make_response, g
from flask_restplus import Resource, Namespace

from controller.schema import job_schema, job_status_schema
from controller.blueprints import valid_roles

ns = Namespace('jobs')


@ns.route('/')
class JobCollection(Resource):
    """Lets you display and add new jobs. """ 

    @valid_roles(['Administrator'])
    def get(self):
        """GET */jobs*

        Jobs of all Users will can listed here. User or team specific entries
        can not be requested here.
         
        **Query String Parameters:**
            
            - **status** - requested jobs will have this status.
              Can be ``ENQUEUED``, ``ACTIVE``, or ``DONE``.
            - **days** - how old the requested jobs can be. Only affects
              the request, if ``status`` is ``DONE``.

        .. note::
           
           The status ACTIVE includes jobs, which are ENQUEUED
        
        :return: A json formatted string with all requested jobs
        """
        status = request.args.getlist(key='status')
        if not status: status = ['DONE']
        days = request.args.get('days', default=12, type=int)
        if not 'DONE' in status: days = None
        app_request = {
                'user': g.username,
                'statuses': status,
                'days': days
                }
        r = current_app.config['APPLICATION'].get_jobs(**app_request)

        return jsonify(r)

    @valid_roles()
    def post(self):
        """POST */jobs*

        Creates a new job.
        
        **JSON Request Parameters:**
        
            - **workspace**(str) - the workspace, which is to be moved
            - **target**(str) - the storage files  will be moved to
            - **a**(bool) - send email to requester upon abortion the job [optional]
            - **b**(bool) - send email to requester upon beginning the job [optional]
            - **e**(bool) - send email to requester upon  ending the job [optional]
            - **for_user**(str) - the user for whom the directory is moved. [optional][restricted to ``Administrator``]

        :return: the unique identifier of the newly created job

        """
        req = job_schema(g.payload)
        role = current_app.config['APPLICATION'].get_user_type(user=g.username)
        if req.get('for_user') and role is not 'Administrator':
            abort(401)
        req['user'] = g.username
        req['email'] = [req.pop('a'), req.pop('b'), req.pop('e')]
        identifier = current_app.config['APPLICATION'].create_job(**req)
        return jsonify(identifier)


@ns.route('/<int:identifier>')
class JobItem(Resource):
    """Lets you display, change and delete ongoing jobs. """

    @valid_roles()
    def get(self, identifier):
        """GET */jobs/<int:job_id>*
        
        Displays information about this job.

        **JSON Response Parameters:**

        - **job_id**(int) - unique identifier
        - **source**(str) - source directory
        - **target**(str) - target directory
        - **enqeue_time** - amount of time the job spent in queue
        - **creator** - person that initiated this job
        - **status**(str) - current status of the job

        """
        answer = current_app.config['APPLICATION'].get_job(user=g.username, job_id=identifier)
        return jsonify(answer)

    @valid_roles(['Administrator'])
    def patch(self, identifier):
        """PUT */jobs/<int:job_id>*
        
        Changes the status of the job.
        
        **JSON Request Parameters:**

        - **status**(str) - changes the status of this job [optional]
        - **priority**(int) - changes the priority of the job and has to be >= 0 [optional]

        .. warning:: 
            Its only allowed to resume a job, you can't pause at the moment,
            so the only valid status argument is 'ACTIVE'.
        """
        args = job_status_schema(g.payload)
        prio = args.get('priority')
        if prio:
            current_app.config['APPLICATION'].set_priority(job_id=identifier, priority=prio)
        if args.get('status') == "ACTIVE":
            current_app.config['APPLICATION'].resume(identifier)
        return make_response(jsonify(''), 204)

    @valid_roles()
    def delete(self, identifier):
        """DELETE */jobs/<int:job_id>*
        
        Deletes this job.
        """
        body = dict(job_id=identifier, user=g.username)
        answer = current_app.config['APPLICATION'].cancel_job(body)
        return jsonify(answer)
