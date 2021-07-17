import pytest
import json

from application.application_adapter import Application
from application.system.user import User, Administrator
from application.system.job import Job, JobStatus
from exceptions.user_not_found_exception import UserNotFoundException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())

"""
Component test! 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_set_priority():
    """
    /SA1010/
    """
    try:
        user = User.get_user_by_username("priorityuser1")
    except UserNotFoundException:
        user = Administrator("priorityuser1", "token")

    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job_id = job.get_job_id()
    job.set_status(JobStatus.QUEUED)

    request = {
        "job_id": job_id,
        "priority": 3
    }

    json_string = json.dumps(request)
    app.set_priority(json_string)

    job = Job.get_job_by_id(job_id)
    assert job.get_priority() == 3
