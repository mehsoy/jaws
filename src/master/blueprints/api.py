""".. module:: api """
from flask_restplus import Api
from flask import Blueprint

from .job_endpoints import ns as jobs
from .worker_endpoints import ns as workers


blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_namespace(jobs)
api.add_namespace(workers)

