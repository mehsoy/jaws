import sys
import pytest
import os

from search.config_handler import ConfigHandler
from exceptions.configuration_exception import ConfigurationException

path = os.getcwd()
c_handler = ConfigHandler(path + '/src/tests/search/test_config.ini')


