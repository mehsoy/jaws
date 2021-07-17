import pytest
import json

from application.application_adapter import Application
from application.system.job import Job, JobStatus
from application.system.user import User, Administrator
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.permission_exception import PermissionException
from exceptions.semantic_exception import SemanticException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master().get_master())
"""
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""

@pytest.mark.order1
def test_cancel_job():
    """
    /SA110/
    """
    try:
        user = User.get_user_by_username("canceljobuser1")
    except UserNotFoundException:
        user = User("canceljobuser1", "token")

    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job_id = job.get_job_id()
    job.set_status(JobStatus.ACTIVE)

    request = {
        "job_id": job_id,
        "user": "canceljobuser1"
    }
    json_string = json.dumps(request)
    app.cancel_job(json_string)
    assert Job.get_job_by_id(job_id).get_status() == JobStatus.CANCELED


@pytest.mark.order2
def test_cancel_job_administrator():
    """
    /SA120/
    """
    try:
        user = User.get_user_by_username("canceljobuser2")
    except UserNotFoundException:
        user = User("canceljobuser2", "token")

    try:
        user = User.get_user_by_username("canceljobadmin2")
    except UserNotFoundException:
        user = Administrator("canceljobadmin2", "token")

    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job_id = job.get_job_id()
    job.set_status(JobStatus.ACTIVE)

    request = {
        "job_id": job_id,
        "user": "canceljobadmin2"
    }
    json_string = json.dumps(request)
    app.cancel_job(json_string)
    assert Job.get_job_by_id(job_id).get_status() == JobStatus.CANCELED


@pytest.mark.order3
def test_cancel_job_wrong_administrator():
    """
    /SA130/
    """
    try:
        user = User.get_user_by_username("canceljobuser3")
    except UserNotFoundException:
        user = User("canceljobuser3", "token")

    try:
        admin = User.get_user_by_username("canceljobfalseadmin33")
    except UserNotFoundException:
        admin = User("canceljobfalseadmin33", "token")

    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job_id = job.get_job_id()
    job.set_status(JobStatus.ACTIVE)

    request = {
        "job_id": job_id,
        "user": "canceljobfalseadmin33"
    }
    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        app.cancel_job(json_string)


@pytest.mark.order4
def test_cancel_job_semantic_exception():
    """
    /SA140/
    """
    try:
        user = User.get_user_by_username("canceljobuser4")
    except UserNotFoundException:
        user = User("canceljobuser4", "token")

    try:
        admin = User.get_user_by_username("canceljobadmin4")
    except UserNotFoundException:
        admin = Administrator("canceljobadmin4", "token")

    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job_id = job.get_job_id()
    job.set_status(JobStatus.DONE)

    request = {
        "job_id": job_id,
        "user": "canceljobadmin4"
    }
    json_string = json.dumps(request)
    with pytest.raises(SemanticException):
        app.cancel_job(json_string)
