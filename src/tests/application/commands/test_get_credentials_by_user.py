import json
import pytest

from application.application_adapter import Application
from application.system.user import User
from exceptions.user_not_found_exception import UserNotFoundException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master
from exceptions.user_not_found_exception import UserNotFoundException

app = Application(SearchHandler(), Master())

"""
Component test! 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


def test_get_credentials_by_user():
    """
    /SA710/
    """
    try:
        user = User.get_user_by_username("creduser")
    except UserNotFoundException:
        user = User("creduser", "token123")

    request = {
        "username": "creduser",
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_credentials_by_user(json_string))

    assert response["token"] == "token123"

    try:
        user = User.get_user_by_username("credadmin")
    except UserNotFoundException:
        user = User("credadmin", "token321")

    request = {
        "username": "credadmin",
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_credentials_by_user(json_string))

    assert response["token"] == "token321"


def test_get_credentials_by_not_existing_user():
    request = {
        "username": "userdoesntexistssdjfhasdjfoasdfoasdhfkljashdfjlhadfkl",
    }

    json_string = json.dumps(request)
    with pytest.raises(UserNotFoundException):
        app.get_credentials_by_user(json_string)

