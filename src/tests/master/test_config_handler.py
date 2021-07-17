import sys
import pytest

from master.config_handler import ConfigHandler
from exceptions.configuration_exception import ConfigurationException

import os
dirname = os.path.dirname(os.path.abspath(__file__))
c_handler1 = ConfigHandler(dirname + '/config1.ini')

@pytest.mark.order1
def test_get_token():
    token = c_handler1.get_token()
    assert token == 'abcd'

@pytest.mark.order2
def test_get_communicator_port():
    token = c_handler1.get_communicator_port()
    assert token == 'kl'

@pytest.mark.order3
def test_active_on_start():
    token = c_handler1.get_active_on_start()
    assert token is True

@pytest.mark.order4
def test_active_on_start():
    with pytest.raises(ConfigurationException):
        c_handler2 = ConfigHandler(dirname + '\config_with_mistake.ini')
