""".. module:: job_endpoints"""
from json import dumps

from flask import request, jsonify, current_app, make_response, g
from flask_restplus import Namespace, Resource
from voluptuous import Schema, Required, Optional, Any

from ..master import Master

ns = Namespace('jobs')
master = Master.get_master()


@ns.route('/<int:job_id>')
class JobItem(Resource):

    def patch(self, job_id):
        body = g.payload
        answer = master.job_changed_status(body)
        return dumps(answer), 204


@ns.route('/<int:job_id>/stats')
class JobItemStats(Resource):

    def post(self, job_id):
        body = job_stats(g.payload)
        master.add_job_stats(job_id=job_id, stats=body)
        return None, 204


job_stats = Schema({
    Optional('total_size', default=None): Any(None, int),
    Optional('n_of_files', default=None): Any(None, int),
    Optional('n_of_dirs', default=None): Any(None, int),
    Optional('compression_rate', default=None): Any(None, int, float)
})
