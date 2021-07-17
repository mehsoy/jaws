import pytest
import json

from application.application_adapter import Application
from application.handlers.search_handler import SearchHandler
from tests.application.mockups.master_test_mockup import Master
from exceptions.permission_exception import PermissionException

app = Application(SearchHandler(), Master())
"""
Integration test Application <-> Search
Master is mocked up
For /ASxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_get_user_credentials():
    """
    /AS210/
    """
    request = {
        "user": "centos",
        "token": "PZ151XH7A1"
    }
    json_string = json.dumps(request)
    response = json.loads(app.verify_user(json_string))

    assert len(response) == 1
    assert response['role'] == "User"


@pytest.mark.order2
def test_get_user_credentials1():
    """
    /AS220/
    """
    request = {
        "user": "centos",
        "token": "PZ151XH7A1FFFFFF"
    }
    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        json.loads(app.verify_user(json_string))
