""".. module:: worker_endpoints"""
import json

from flask import request, jsonify, make_response, g, Response
from flask_restplus import Namespace, Resource

from ..master import Master


ns = Namespace('workers')
master = Master.get_master()

@ns.route('/')
class WorkerCollection(Resource):

    def post(self):
        answer = master.register_worker(g.payload)
        return jsonify(answer)

@ns.route('/<string:worker_name>')
class WorkerItem(Resource):

    def patch(self, worker_name):
        body = g.payload
        body['worker_name'] = worker_name
        # Generator pattern is needed to invoke function worker_changed_status only after the response
        # has been sent to worker. This prevents a deadlock in the worker.
        def gen():
            yield jsonify('')
            master.worker_changed_status(body)
        return Response(gen())
