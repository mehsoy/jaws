#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import toml

from configparser import ConfigParser
from application.system.user_role import UserRole

from helpers import get_conf_directory, Singleton


class ACLConfigHandler(metaclass=Singleton):
    """
    Represents config file as permanently living object - singleton
    """
    conf_dir = get_conf_directory()
    default_config_file = conf_dir + 'application/acl.toml'

    def __init__(self, config_file=None):
        """The Constructor"""
        self.config_file = config_file if config_file else self.default_config_file

    def get_workspaces_setter_acl(self):
        return self.get_setter_acl_for('workspaces')

    def get_storages_setter_acl(self):
        return self.get_setter_acl_for('storages')

    def get_setter_acl_for(self, table):
        config = toml.load(self.config_file)

        setter_acl = dict()
        setter_acl[UserRole.User] = config.get(table).get('User')
        setter_acl[UserRole.Administrator] = config.get(table).get('Administrator')
        return setter_acl