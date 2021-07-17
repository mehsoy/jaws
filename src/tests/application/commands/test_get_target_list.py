import pytest
import json

from application.application_adapter import Application
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())
"""
Component test! 
Search Handler should be mocked up 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_get_target_list():
    """
    /SA810/
    """
    response = json.loads(app.get_target_list())

    assert len(response) == 1
    assert len(response['targets']) == 3
    assert response['targets'][0] == "storage1"
    assert response['targets'][1] == "storage2"
    assert response['targets'][2] == "storage3"
