""".. module:: schema """
import re
from voluptuous import Schema, Invalid, Required, Any, All
from application.system.user_role import UserRole

"""Contains all schemata used in controller package

``Schema`` objects are used validate incoming JSON formatted 
requests.
"""

#Validators for schemata
def Role(value):
    if value in [color.name for color in UserRole]:
        return value
    else:
        raise Invalid('Role doesnt exist.')

def Status(value):
    if value == 'ACTIVE' or value == 'DEACTIVATED':
        return value
    else:
        raise Invalid('Bad Request: Status has to be either ACTIVE or DEACTIVATED!')

def Instruction(value):
    perm_pattern = re.compile('[+-=][rwx-]{0,3}')
    if perm_pattern.match(value):
        return value
    else:
        raise Invalid('Bad Request: invalid instruction syntax.')

def Tag_Type(value):
    if value in ['user', 'group', 'other']:
        return value
    else:
        raise Invalid('Bad Request: invalid instruction syntax.')

#Schemata are defined here
job_schema = Schema({
    Required('workspace'): str,
    Required('target'): str,
    Required('a', default=False): bool,
    Required('b', default=False): bool,
    Required('e', default=False): bool,
    Required('for_user', default=None): Any(None, str),
})

job_status_schema = Schema({
    'priority': int,
    'status': Status,
})

binary_status_schema = Schema({
    Required('status'): Status,
})

role_schema = Schema({
    Required('role'): Role,
})

patch_access_schema = Schema({
    Required('tag_type'): Tag_Type,
    Required('name', default=None): object,
    Required('instruction'): Instruction,
})

