from flask import Blueprint, jsonify, make_response
from voluptuous import Invalid

from exceptions.permission_exception import PermissionException
from exceptions.no_response_from_worker_exception import NoResponseFromWorkerException 
#from exceptions.worker_busy_exception import WorkerBusyException
#from exceptions.worker_crashed_exception import WorkerCrashedException


blueprint = Blueprint('errors', __name__)


@blueprint.errorhandler(Invalid)
def invalid_handler(e):
    return make_response(jsonify(e), 422)

@blueprint.errorhandler(PermissionException)
def permission_handler(e):
    return make_response(jsonify(e), 403)

@blueprint.errorhandler(NoResponseFromWorkerException)
def no_response_from_worker_handler(e):
    return make_response(jsonify(e), 503)

#@blueprint.errorhandler(WorkerBusyException)
#def worker_busy_handler(e):
#    return make_response(jsonify(e), 503)
#
#@blueprint.errorhandler(WorkerCrashedException)
#def worker_crashed_handler(e):
#    return jsonify(e), 503
            
             
             
