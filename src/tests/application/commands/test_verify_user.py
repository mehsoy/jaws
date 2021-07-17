import json
import pytest

from application.application_adapter import Application
from application.system.user import User
from application.system.user import Administrator
from exceptions.user_not_found_exception import UserNotFoundException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master
from exceptions.permission_exception import PermissionException

app = Application(SearchHandler(), Master())

"""
Component test! 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


def test_verify_user():
    """
    /SA1110/
    """
    try:
        user = User.get_user_by_username("verifyadmin")
    except UserNotFoundException:
        user = Administrator("verifyadmin", "token3")

    request = {
        "user": "verifyadmin",
        "token": "token3"
    }

    json_string = json.dumps(request)
    response = json.loads(app.verify_user(json_string))

    assert response["role"] == "Administrator"


def test_verify_admin():
    """
    /SA1120/
    """
    try:
        user = User.get_user_by_username("verifyuser")
    except UserNotFoundException:
        user = User("verifyuser", "token2")

    request = {
        "user": "verifyuser",
        "token": "token2"
    }

    json_string = json.dumps(request)
    response = json.loads(app.verify_user(json_string))

    assert response["role"] == "User"


def test_verify_user_exceptions():
    """
    /SA1130/
    """
    # Invalid token given
    try:
        user = User.get_user_by_username("verifyadmin")
    except UserNotFoundException:
        user = Administrator("verifyadmin", "token3")

    request = {
        "user": "verifyadmin",
        "token": "invalidtoken"
    }

    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        app.verify_user(json_string)

    """
    /SA1140/
    """
    # Invalid token in database
    try:
        user = User.get_user_by_username("uyefv")
    except UserNotFoundException:
        user = User("uyefv", "token3")

    request = {
        "user": "uyefv",
        "token": "token1"
    }

    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        app.verify_user(json_string)
