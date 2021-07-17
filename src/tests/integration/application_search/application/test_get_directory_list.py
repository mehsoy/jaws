import pytest
import json

from application.application_adapter import Application
from application.system.user import User
from application.handlers.search_handler import SearchHandler
from tests.application.mockups.master_test_mockup import Master
from exceptions.user_not_found_exception import UserNotFoundException

app = Application(SearchHandler(), Master())
"""
Integration test Application <-> Search
Master is mocked up
For /ASxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_get_directory():
    """
    /AS010/
    """
    try:
        user1 = User.get_user_by_username("user1ldap")
    except UserNotFoundException:
        user1 = User("user1ldap", "token")

    request = {
        "target": "archive1",
        "user": "user1ldap",
        "for_user": "user1ldap"
    }
    json_string = json.dumps(request)
    response = json.loads(app.get_directory_list(json_string))
    assert len(response) == 1
    assert len(response['archive1']) == 2
    assert response['archive1'][0] == "/user1ldap-first_directory"
    assert response['archive1'][1] == "/user1ldap-second_directory"


@pytest.mark.order2
def test_get_directory2():
    """
    /AS020/
    """
    try:
        user1 = User.get_user_by_username("user1ldap")
    except UserNotFoundException:
        user1 = User("user1ldap", "token")

    request = {
        "target": "",
        "user": "user1ldap",
        "for_user": "user1ldap"
    }
    json_string = json.dumps(request)
    response = json.loads(app.get_directory_list(json_string))
    print(response)
    assert len(response) == 4
    assert len(response['archive1']) == 2
    assert response['archive1'][0] == "/user1ldap-first_directory"
    assert response['archive1'][1] == "/user1ldap-second_directory"

    assert len(response['centos']) == 3
    assert response['centos'][0] == "/user1ldap-memories-1"
    assert response['centos'][1] == "/user1ldap-memories-2"
    assert response['centos'][2] == "/user1ldap-experiments-1"
