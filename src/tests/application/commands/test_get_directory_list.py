import pytest
import json

from application.application_adapter import Application
from application.system.user import User, Administrator
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.permission_exception import PermissionException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())
"""
Component test! 
Search Handler should be mocked up 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_get_directory_list():
    """
    1. Administrator requests directory list of another user /SA610/
    2. User requests his own directory list /SA620/
    3. Another user (not Administrator) requests directory list of user /SA630/
    """
    try:
        admin = User.get_user_by_username("diradmin")
    except UserNotFoundException:
        admin = Administrator("diradmin", "token")

    try:
        user1 = User.get_user_by_username("diruser1")
    except UserNotFoundException:
        user1 = User("diruser1", "token")

    try:
        user2 = User.get_user_by_username("diruser2")
    except UserNotFoundException:
        user2 = User("diruser2", "token")

    # --------1--------
    request = {
        "target": "testtarget",
        "user": "diradmin",
        "for_user": "diruser1"
    }
    json_string = json.dumps(request)
    response = json.loads(app.get_directory_list(json_string))

    assert len(response) == 1
    assert len(response['testtarget']) == 3
    assert response['testtarget'][0] == "directory1"
    assert response['testtarget'][1] == "directory2"
    assert response['testtarget'][2] == "directory3"

    # --------2--------

    request = {
        "target": "testtarget",
        "user": "diruser1",
        "for_user": "diruser1"
    }
    json_string = json.dumps(request)
    response = json.loads(app.get_directory_list(json_string))

    assert len(response) == 1
    assert len(response['testtarget']) == 3
    assert response['testtarget'][0] == "directory1"
    assert response['testtarget'][1] == "directory2"
    assert response['testtarget'][2] == "directory3"

    # --------3--------

    request = {
        "target": "testtarget",
        "user": "diruser2",
        "for_user": "diruser1"
    }
    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        json.loads(app.get_directory_list(json_string))

