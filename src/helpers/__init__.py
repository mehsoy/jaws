import os
from configparser import ConfigParser, RawConfigParser
from flask import request, g, Response
import requests
from json import dumps, loads
from pymunge import MungeContext


curr_dirname = os.path.dirname(os.path.abspath(__file__))
src_dir, _ = os.path.split(curr_dirname)
file = src_dir + '/dev_config.ini'

def use_munge():
    cp = ConfigParser()
    cp.read(file)
    return cp['GLOBAL'].getboolean('munge')

def munge_response(response):
    if use_munge():
        body = response.json
        payload = dumps(body).encode('utf-8')
        with MungeContext() as ctx:
            cred = ctx.encode(payload).decode('utf-8')
        json = dumps(dict(munge_cred=cred))
        response.data = json
        return response
    else:
        return response

def unmunge_request():
    body = request.json
    if use_munge():
        cred = body['munge_cred'].encode('utf-8')
        with MungeContext() as ctx:
            payload, uid, gid = ctx.decode(cred)
        g.payload = loads(payload.decode('utf-8'))
    else:
        g.payload = body

def send_request(*args, **kwargs) -> (Response, str):
    if not kwargs.get('json'):
        kwargs['json'] = dict()
    if use_munge():
        with MungeContext() as ctx:
            cred = ctx.encode(dumps(kwargs['json']).encode('utf-8')).decode('utf-8')
        kwargs['json'] = dict(munge_cred=cred)
        r = requests.request(*args, **kwargs)
        if r.text:
            return r, loads(unmunge(r.text))
        else:
            return r, r.text
    else:
        r = requests.request(*args, **kwargs)
        return r, loads(r.text)

def unmunge(text):
    if use_munge():
        d = loads(text)
        cred = d['munge_cred'].encode('utf-8')
        with MungeContext() as ctx:
            payload, uid, guid = ctx.decode(cred)
        return payload.decode('utf-8')
    else:
        return text


def get_conf_directory():
    default_config = '/etc/default/dmd'
    home_dir = os.path.expanduser("~")  + '/.dmd/'
    project_cfg = os.getcwd() + '/src/cfg/'

    if os.path.isfile(default_config):
        with open(default_config) as f:
            file_content = '[dummy_section]\n' + f.read()
        config_parser = RawConfigParser()
        config_parser.read_string(file_content)
        return config_parser.get('dummy_section', 'conf_directory')
    elif os.path.isfile(home_dir + 'controller'):
        return home_dir
    else:
        return project_cfg

def get_configfile_from_config(configuration):
    default_config = '/etc/default/jaws'
    project_cfg = os.getcwd() + '/src/cfg/'
    path = ""
    config_file = ""
    if os.path.isfile(default_config):
        with open(default_config) as f:
            file_content = '[dummy_section]\n' + f.read()
        config_parser = RawConfigParser()
        config_parser.read_string(file_content)
        path = config_parser.get('dummy_section', 'conf_directory')
    else:
        path =  project_cfg
    main_parser = ConfigParser()
    main_config = main_parser.read(path + 'main.ini')
    if configuration == "storages":
        config_file = main_parser.get('CONFIGFILES', 'STORAGES')
    if configuration == "acl":
        config_file = main_parser.get('CONFIGFILES', 'ACL')
    if configuration == "application":
        config_file = main_parser.get('CONFIGFILES', 'APPLICATION')
    if configuration == "copytools":
        config_file = main_parser.get('CONFIGFILES', 'COPYTOOLS')
    if configuration == "controller":
        config_file = main_parser.get('CONFIGFILES', 'CONTROLLER')
    if configuration == "master":
        config_file = main_parser.get('CONFIGFILES', 'MASTER')
    if configuration == "view":
        config_file = main_parser.get('CONFIGFILES', 'MASTER')
    if configuration == "worker":
        config_file = main_parser.get('CONFIGFILES', 'WORKER')
    if configuration == "main":
        config_file = path + 'main.ini'

    config = ConfigParser()
    config.read(path + config_file)

    configuration_sections = config.sections()
    configuration = dict()

    for section in configuration_sections:
        configuration[section] = dict(config.items(section))

    return configuration



class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
