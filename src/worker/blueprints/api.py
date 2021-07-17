""".. module:: api """
from flask_restplus import Api
from flask import Blueprint

from .task_endpoints import ns as task
from .worker_endpoints import ns as workers

blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_namespace(task)
api.add_namespace(workers)

