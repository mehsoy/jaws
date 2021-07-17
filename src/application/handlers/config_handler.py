#!/usr/bin/python
#-*- coding: utf-8 -*-
import os

from configparser import ConfigParser
from application.system.storage import Storage
from exceptions.incorrect_config_file_error import IncorrectConfigFileError

from exceptions.configuration_exception import ConfigurationException
from helpers import get_conf_directory, Singleton, get_configfile_from_config


class ConfigHandler(metaclass=Singleton):
    """
    Represents config file as permanently living object - singleton
    """
    conf_dir = get_conf_directory()
    default_config_file = conf_dir + 'application/config.ini'

    def __init__(self, config_file=None):
        """The Constructor"""
        config_file = config_file if config_file else self.default_config_file
        _config = ConfigParser()
        self.config = _config
        _config.read(config_file)

        self._emails_for_errors = _config.get('Configuration', 'emails_for_errors').split(', ')
        self._administrators = _config.get('Configuration', 'administrators').split(', ')
        self._email_domain = _config.get('Configuration', 'email_domain')
        self.workspace_default_storage = _config.get('Configuration', 'workspace_default_storage')
        self.delimiter = _config.get('Configuration', 'delimiter')
        self.username_loc = int(_config.get('Configuration', 'username_loc'))
        self.label_loc = int(_config.get('Configuration', 'label_loc'))
        self.number_loc = int(_config.get('Configuration', 'number_loc'))
        self.action_log_path = _config.get('Configuration', 'action_log_path')
        #[Workspaces]
        # freetext = ""
        # dummy = 3
        # freetext2 = "nothing"
        workspace_options = []
        for option in _config['Workspaces']:
            dummy = {option :_config['Workspaces'][option] }
            workspace_options.append(dummy)
            #workspace_options[option] = _config['Workspaces'][option]
        setattr(self, "workspace_options",workspace_options)

        try: 
            self._max_tasks_number_for_user = _config.getint('Configuration', 'max_tasks_number_for_user')
        except ValueError as exc:
            raise ConfigurationException('max_tasks_number_for_user', 'Application') from exc

        try: 
            self._logs_storage_duration = _config.getint('Configuration', 'logs_storage_duration')
        except ValueError as exc:
            raise ConfigurationException('logs_storage_duration', 'Application') from exc

    def get_emails_for_errors(self, ):
        """Returns e-mails to which a message with information in case of problems will be sent"""
        return self._emails_for_errors 

    def get_logs_storage_duration(self, ):
        """Returns number of days how long the logs will be stored in system"""
        return self._logs_storage_duration 

    def get_max_tasks_number_for_user(self, ):
        """Returns number of jobs the user is allowed to execute simultaneously"""
        return self._max_tasks_number_for_user

    def get_administrators(self, ):
        """Returns list of administrators in system"""
        return self._administrators

    def get_email_domain(self):
        """Returns email domain for notifications"""
        return self._email_domain

    def get_workspace_options(self):
        return self.workspace_options

    def assemble_workspace_full_name(self, username, workspacename, number):
        vector = [0, 0, 0]
        vector[self.username_loc] = username
        vector[self.label_loc] = workspacename
        vector[self.number_loc] = str(number)
        return self.delimiter.join(vector)

    def disassemble_workspace_name(self, name):
        vec = name.split(self.delimiter)
        return vec[self.label_loc], vec[self.number_loc]

    def disassemble_workspace_full_name(self, full_name):
        vec = full_name.split(self.delimiter)
        return vec[self.username_loc], vec[self.label_loc], vec[self.number_loc]


def initialize_storages_from_config():
    config_path = get_conf_directory() + 'application/storages.ini'

    if not os.path.exists(config_path): raise IncorrectConfigFileError('Configuration file not found')
    if not (config_path[-4:] == ".ini"): raise IncorrectConfigFileError('Configuration file is in the wrong format')

    _config = ConfigParser()
    _config.read(config_path)

    storages_sections = _config.sections()
    storages = dict()

    for section in storages_sections:
          alias = _config.get(section, 'alias')
          mountpoint = _config.get(section, 'mountpoint')
          has_home_path = _config.getboolean(section, 'has_home_path')
          is_archive = _config.getboolean(section, 'is_archive')
          storage_type = _config.get(section, 'type')
          max_extensions = int(_config.get(section, 'max_extensions'))
          max_extension_period = int(_config.get(section, 'max_extension_period'))
          description = _config.get(section, 'description')
          if not Storage.get_storage_by_name(alias):
              Storage(alias, mountpoint, True, has_home_path,
                    is_archive, max_extensions, max_extension_period, description)

    return storages

def get_storages_configuration():
    config_path = get_conf_directory() + 'application/storages.ini'

    if not os.path.exists(config_path): raise IncorrectConfigFileError('Configuration file not found')
    if not (config_path[-4:] == ".ini"): raise IncorrectConfigFileError('Configuration file is in the wrong format')

    _config = ConfigParser()
    _config.read(config_path)

    storages_sections = _config.sections()
    #storages = dict()
    storages = dict()

    for section in storages_sections:
        #storages[section] = dict(_config.items(section))
        storages[section] = dict(_config.items(section))

    return storages

def get_controller_configuration():
    config_path = get_conf_directory() + 'controller/config.ini'

    if not os.path.exists(config_path): raise IncorrectConfigFileError('Configuration file not found')
    if not (config_path[-4:] == ".ini"): raise IncorrectConfigFileError('Configuration file is in the wrong format')

    _config = ConfigParser()
    _config.read(config_path)

    controller_sections = _config.sections()
    controller = dict()

    for section in controller_sections:
        #storages[section] = dict(_config.items(section))
        controller[section] = dict(_config.items(section))

    return controller

def get_ini_configuration(configuration):
    """
    Returns the configuration file as nested dict
    :param configuration: which configuration to parse
    :return: parsed configurations as nested dict ([section] -> [Key:Values])
    """
    # STORAGES = cfg / application / storages.ini
    # ACL = cfg / application / acl.toml
    # APPLICATION = cfg / application / config.ini
    # COPYTOOLS = cfg / application / copytools.ini
    # CONTROLLER = cfg / controller / config.ini
    # MASTER = cfg / master / config.ini
    # VIEW = cfg / view / config.ini
    # WORKER = cfg / worker / config.ini
    # GLOBAL = dev_config.ini
#TODO fix ACL Parser

    config_path = get_conf_directory()
    config_content = []
    if configuration == "storages":
        config_content = get_configfile_from_config('storages')
    elif configuration == "acl":
        config_content = get_configfile_from_config('acl')
    elif configuration == "application":
        config_content = get_configfile_from_config('application')
    elif configuration == "copytools":
        config_content = get_configfile_from_config('copytools')
    elif configuration == "controller":
        config_content = get_configfile_from_config('controller')
    elif configuration == "master":
        config_content = get_configfile_from_config('master')
    elif configuration == "view":
        config_content = get_configfile_from_config('view')
    elif configuration == "worker":
        config_content = get_configfile_from_config('worker')
    elif configuration == "main":
        config_content = get_configfile_from_config('main')
    else:
        raise IncorrectConfigFileError('Configuration file not found')

    return config_content