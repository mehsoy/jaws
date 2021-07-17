#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import configparser
import getpass

from helpers import get_conf_directory


class Tokenify:
    """
        Tokenify class with static help methodes
    """

    @staticmethod
    def getUsername():
        """
        get's the username
        :return: username
        """
        return getpass.getuser()

    @staticmethod
    def getToken():
        """
        get's the credential
        :return: the credential string
        """

        credentials = open(os.path.join(os.path.expanduser("~"), '.dmd', 'config', 'credentials.txt'))
        string = credentials.readline()
        credentials.close()
        return string.rstrip()

    @staticmethod
    def get_url():
        """
        get's the controller url
        :return: the controller url
        """
        conf_dir = get_conf_directory()
        abs_conf_path = conf_dir + 'view/config.ini'
        config = configparser.ConfigParser()
        config.read(abs_conf_path)
        controller_url = config.get('General Configuration', 'controller_url')

        return controller_url
