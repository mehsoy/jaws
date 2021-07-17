import os
import configparser

from exceptions.configuration_exception import ConfigurationException
from helpers import Singleton
from worker.copytool.rsync import Rsync
from worker.copytool.shiftc import Shiftc
from worker.copytool.tar import Tar


class ToolConfigParser(metaclass=Singleton):

    def __init__(self, config_path=None):
        self._config_path = config_path
        if not config_path or not os.path.exists(config_path):
            raise ConfigurationException(' '.join(['File', config_path, 'doesn\'t exist']))

        cp = configparser.ConfigParser()
        cp.read(config_path)

        if 'tools' in cp.sections():
            self._tools = cp['tools']
        else:
            raise ConfigurationException('No section \'tools\' in' + config_path)

    def get_executable_path(self, identifier: str):
        if identifier in self._tools:
            return self._tools.get(identifier)
        else:
            raise ConfigurationException(' '.join(['Field', identifier, 'doesn\'t exist in', self._config_path]))

    def get_copytool_class(self, name):
        i = dict(tar=Tar,
                 rsync=Rsync,
                 shiftc=Shiftc)
        return i[name]