from voluptuous import Schema, Required, Any

from exceptions.configuration_exception import ConfigurationException


def storage_type(string: str):
    if string in ['posix', 'archive', 'tape']:
        return string
    else:
        raise ConfigurationException(''.join([string, 'is not a valid storage type.']))


validate_general = Schema({
    Required('worker_name'): str,
    Required('worker_address'): str,
    Required('master_address'): str,
    Required('reconnect_timeout'): int,
    Required('reconnect_frequency'): int,
    Required('authentification_token'): str,
    Required('mountpoints'): list,
})
