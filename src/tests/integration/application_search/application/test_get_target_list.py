import pytest
import json

from application.application_adapter import Application
from application.handlers.search_handler import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())
"""
Integration test Application <-> Search
Master is mocked up
For /ASxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_get_target_list():
    """
    /AS110/
    """
    response = json.loads(app.get_target_list())

    assert len(response) == 1
    assert len(response['targets']) == 4
    assert response['targets'][0] == "archive1"
    assert response['targets'][1] == "centos"
    assert response['targets'][2] == "dmd5"
    assert response['targets'][3] == "dmd_home"

