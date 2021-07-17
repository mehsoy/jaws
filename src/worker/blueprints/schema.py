""".. module:: schema"""
from voluptuous import Schema, Required, Invalid

#Validators for schemata
def Status(value):
    if value == 'ACTIVE' or value == 'DEACTIVATED':
        return value
    else:
        raise Invalid('Bad Request: Status has to be either ACTIVE or DEACTIVATED!')

#Schemata are defined here
job_schema = Schema({
    Required('user_name'): str,
    Required('job_id'): int,
    Required('source_path'): str,
    Required('target_path'): str,
}, extra=True)


binary_status_schema = Schema({
    Required('status'): Status,
})


