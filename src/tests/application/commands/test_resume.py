import pytest
import json

from application.application_adapter import Application
from application.system.user import User
from application.system.job import Job, JobStatus
from exceptions.job_not_found_exception import JobNotFoundException
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.semantic_exception import SemanticException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())

"""
Component test! 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


def test_resume():
    """
    /SA910/
    """
    try:
        user = User.get_user_by_username("resumeuser")
    except UserNotFoundException:
        user = User("resumeuser", "token")
    job = Job('storageA', 'storageB', '~/.data/', [True, False, True], user)
    job.set_status(JobStatus.PAUSED)
    job_id = job.get_job_id()

    request = {
        "job_id": job_id,
    }
    json_string = json.dumps(request)
    app.resume(json_string)


def test_resume_exception():
    """
    /SA920/
    """
    try:
        user = User.get_user_by_username("resumeuser")
    except UserNotFoundException:
        user = User("resumeuser", "token")
    job = Job('storageA', 'storageB', '~/.data/', [True, False, True], user)
    job.set_status(JobStatus.ACTIVE)
    job_id = job.get_job_id()

    request = {
        "job_id": job_id,
    }
    json_string = json.dumps(request)
    with pytest.raises(SemanticException):
        app.resume(json_string)

    """
    /SA930/
    """

    request = {
        "job_id": "87497294723947289374823[7936593653456348756t3487657834658723452345",
    }
    json_string = json.dumps(request)
    with pytest.raises(JobNotFoundException):
        app.resume(json_string)


