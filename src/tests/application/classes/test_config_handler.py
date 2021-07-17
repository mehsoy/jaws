import sys
import pytest
import os

sys.path.append('../../')

from application.handlers.config_handler import ConfigHandler
from exceptions.configuration_exception import ConfigurationException

path = os.getcwd()



@pytest.mark.order1
def test_get_emails_for_errors():
    """Test getters"""
    c_handler1 = ConfigHandler(path + '/src/tests/application/config.ini')
    #assert c_handler1.get_emails_for_errors() == ['e1@test.com', 'e2@test.com', 'e3@test.com']
    assert c_handler1.get_logs_storage_duration() == 30
    assert c_handler1.get_max_tasks_number_for_user() == 3
    assert c_handler1.get_administrators() == ['ldap1', 'ldap2', 'ldap3']
    assert c_handler1.get_search_address() == 'klmno'


@pytest.mark.order2
def test_wrong_max_number():
    """Test wrong max_tasks_number_for_user value (not int)"""
    with pytest.raises(ConfigurationException):
        c_handler = ConfigHandler(path + '/src/tests/application/config_with_wrong_max_tasks_number.ini')

@pytest.mark.order3
def test_wrong_logs_duration():
    """Test wrong _logs_storage_duration value (not int)"""
    with pytest.raises(ConfigurationException):
        c_handler = ConfigHandler(path + '/src/tests/application/config_with_wrong_logs_duration.ini')
