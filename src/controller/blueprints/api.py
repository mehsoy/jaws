""".. module:: api """
from flask_restplus import Api
from flask import Blueprint, jsonify
from voluptuous import Invalid

from exceptions.job_not_found_exception import JobNotFoundException
from exceptions.no_administrator_rights_exception import NoAdministratorRightsException
from exceptions.no_project_manager_rights_exception import NoProjectManagerRightsException
from exceptions.no_response_from_search_exception import NoResponseFromSearchException
from exceptions.permission_exception import PermissionException
from exceptions.semantic_exception import SemanticException
from exceptions.source_path_not_valid_exception import SourcePathNotValidException
from exceptions.storage_alias_not_found_exception import StorageAliasNotFoundException
from exceptions.storage_not_accepting_exception import StorageNotAcceptingException
from exceptions.storage_not_mounted_error import StorageNotMountedError
from exceptions.storage_type_compatibility_exception import StorageTypeCompatibilityException
from exceptions.no_response_from_search_exception import NoResponseFromSearchException
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.master_paused_exception import MasterPausedException
from functools import wraps

from .storage_endpoints import ns as storages
from .job_endpoints import ns as jobs
from .master_endpoints import ns as master
from .worker_endpoints import ns as workers
from .user_endpoints import ns as users
#from application.application_adapter import Application
from .workspace_endpoints import ns as workspaces
from .configuration_endpoints import ns as configuration


"""Combines namespaces into a single object.

The endpoint modules of the API are bundled together to a blueprint, which is
going to be registered to the flask app in controller_initializer. All end-
points in this ``api`` are prefixed in the url with /api.
"""

def default_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
        except Exception as e:
            r = jsonify(str(e))
            r.status_code = 500 if not hasattr(e, 'code') else e.code
        return r
    return wrapper


blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, decorators=[default_error_handler])

api.add_namespace(storages)
api.add_namespace(jobs)
api.add_namespace(master)
api.add_namespace(workers)
api.add_namespace(users)
api.add_namespace(workspaces)
api.add_namespace(configuration)


