import os
import pytest

from exceptions.configuration_exception import ConfigurationException
from worker.tool_config_parser import ToolConfigParser



def test_happy_path(copytools_path):
    tool_parser = ToolConfigParser(copytools_path)
    assert tool_parser.get_executable_path('rsync') == '/usr/bin/rsync'
    assert tool_parser.get_executable_path('tar') == '/bin/tar'

def test_missing_section():
    path = os.getcwd() + '/src/tests/worker/config_handling/corrupted_copytools.ini'
    with pytest.raises(ConfigurationException):
        ToolConfigParser(path)

def test_non_existent_file():
    path = os.getcwd() + '/src/tests/worker/config_handling/non_existent.ini'
    with pytest.raises(ConfigurationException):
        ToolConfigParser(path)

def test_non_existent_identifier():
    path = os.getcwd() + '/src/tests/worker/config_handling/copytools.ini'
    tool_parser = ToolConfigParser(path)
    with pytest.raises(ConfigurationException):
        tool_parser.get_executable_path('non_existent_tool')


