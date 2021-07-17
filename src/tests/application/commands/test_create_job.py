import pytest
import json

from application.application_adapter import Application
from application.system.job import Job, JobStatus
from application.system.user import User, Administrator
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.permission_exception import PermissionException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())
"""
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""

@pytest.mark.order1
def test_create_job():
    """
    /SA010/
    """
    try:
        user = User.get_user_by_username("createjobuser1")
    except UserNotFoundException:
        user = User("createjobuser1", "token")

    request = {
        "source": "source",
        "target": "target",
        "user": "createjobuser1",
        "for_user": "createjobuser1",
        "email": [True, True, True]
    }

    json_string = json.dumps(request)
    job_id = app.create_job(json_string)
    job = Job.get_job_by_id(job_id)
    assert job.get_job_id() == job_id
    assert job.has_start_notification()
    assert job.has_end_notification()
    assert job.has_error_notification()
    assert job.get_target_alias() == "target"

def test_create_job_admin():
    """
    /SA020/
    """
    try:
        user = User.get_user_by_username("createjobuser4")
    except UserNotFoundException:
        user = User("createjobuser4", "token")

    try:
        admin = User.get_user_by_username("admin1")
    except UserNotFoundException:
        admin = Administrator("admin1", "token")

    request = {
        "source": "source",
        "target": "target",
        "user": "admin1",
        "for_user": "createjobuser4",
        "email": [True, True, False]
    }

    json_string = json.dumps(request)
    job_id = app.create_job(json_string)
    job = Job.get_job_by_id(job_id)
    assert job.get_job_id() == job_id
    assert job.has_start_notification()
    assert not job.has_end_notification()
    assert job.has_error_notification()
    assert job.get_target_alias() == "target"
    assert job.get_user().get_username() == "createjobuser4"


def test_create_job_permission_exception():
    """
    /SA030/
    """
    try:
        user = User.get_user_by_username("createjobuser4")
    except UserNotFoundException:
        user = User("createjobuser4", "token")

    try:
        admin = User.get_user_by_username("false_admin1")
    except UserNotFoundException:
        admin = User("false_admin1", "token")

    request = {
        "source": "source",
        "target": "target",
        "user": "false_admin1",
        "for_user": "createjobuser4",
        "email": [True, True, False]
    }

    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        app.create_job(json_string)


def test_create_job_config_exception():
    """Test for max. allowed number of active jobs per user"""
    """
    /SA040/
    """
    try:
        user = User.get_user_by_username("createjobuser2")
    except UserNotFoundException:
        user = User("createjobuser2", "token")

    request = {
        "source": "source",
        "target": "target",
        "user": "createjobuser2",
        "for_user": "createjobuser2",
        "email": [True, True, True]
    }

    json_string = json.dumps(request)

    try:
        job_id = app.create_job(json_string)
        job = Job.get_job_by_id(job_id)
        job.set_status(JobStatus.QUEUED)
    except PermissionException:
        pass

    try:
        job_id = app.create_job(json_string)
        job = Job.get_job_by_id(job_id)
        job.set_status(JobStatus.QUEUED)
    except PermissionException:
        pass

    try:
        job_id = app.create_job(json_string)
        job = Job.get_job_by_id(job_id)
        job.set_status(JobStatus.QUEUED)
    except PermissionException:
        pass

    try:
        job_id = app.create_job(json_string)
        job = Job.get_job_by_id(job_id)
        job.set_status(JobStatus.QUEUED)
    except PermissionException:
        pass

    try:
        job_id = app.create_job(json_string)
        job = Job.get_job_by_id(job_id)
        job.set_status(JobStatus.QUEUED)
        assert 1 == 0
    except PermissionException:
        assert 1 == 1

