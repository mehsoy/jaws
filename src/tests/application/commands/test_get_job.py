import pytest
import json
import datetime

from application.application_adapter import Application
from application.system.user import User, Administrator
from application.system.job import Job, JobStatus
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.no_project_manager_rights_exception import NoProjectManagerRightsException
from tests.application.mockups.search_handler_test_mockup import SearchHandler
from tests.application.mockups.master_test_mockup import Master

app = Application(SearchHandler(), Master())

"""
Component test! 
For /SAxx0/ notation see documentation/Qualitätssicherung.pdf
"""


@pytest.mark.order1
def test_get_job():
    """
    1. Administrator requests job of User /SA510/
    2. User requests his own job /SA520/
    3. Administrator requests his own job /SA530/
    4. User (not Administrator) requests job of another User => Exception /SA540/
    5. User requests job of Administrator => Exception /SA550/
    """
    timestamp = datetime.datetime.now()

    try:
        admin = User.get_user_by_username("jobadmin")
    except UserNotFoundException:
        admin = Administrator("jobadmin", "token")
    job1 = Job('storageA', 'storageB', '~/.data/', [True, False, True], admin)
    job1.set_enqueue_time(timestamp)
    job1.set_status(JobStatus.ACTIVE)
    job1_id = job1.get_job_id()

    try:
        user1 = User.get_user_by_username("jobuser1")
    except UserNotFoundException:
        user1 = User("jobuser1", "token")
    job2 = Job('storageA', 'storageB', '~/.data/', [True, False, True], user1)
    job2.set_enqueue_time(timestamp)
    job2.set_status(JobStatus.DONE)
    job2_id = job2.get_job_id()

    try:
        user2 = User.get_user_by_username("jobuser2")
    except UserNotFoundException:
        user2 = User("jobuser2", "token")
    job3 = Job('storageA', 'storageB', '~/.data/', [True, False, True], user2)
    job3.set_enqueue_time(timestamp)
    job3.set_status(JobStatus.DONE)
    job3_id = job3.get_job_id()

    # -------1--------
    request = {
        "user": "jobadmin",
        "job_id": job2_id
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_job(json_string))

    job = Job.get_job_by_id(job2_id)
    assert len(response) == 6
    assert response['job_id'] == job.get_job_id()
    assert response['source'] == job.get_source_alias() + ":" + job.get_source_relative_path()
    assert response['enqueue_time'] == job.get_enqueue_time().isoformat()
    assert response['creator'] == job.get_user().get_username()
    assert response['status'] == job.get_status().name

    # ------2-------
    request = {
        "user": "jobuser2",
        "job_id": job3_id
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_job(json_string))

    job = Job.get_job_by_id(job3_id)
    assert len(response) == 6
    assert response['job_id'] == job.get_job_id()
    assert response['source'] == job.get_source_alias() + ":" + job.get_source_relative_path()
    assert response['enqueue_time'] == job.get_enqueue_time().isoformat()
    assert response['creator'] == job.get_user().get_username()
    assert response['status'] == job.get_status().name

    # ------3-------
    request = {
        "user": "jobadmin",
        "job_id": job1_id
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_job(json_string))

    job = Job.get_job_by_id(job1_id)
    assert len(response) == 6
    assert response['job_id'] == job.get_job_id()
    assert response['source'] == job.get_source_alias() + ":" + job.get_source_relative_path()
    assert response['enqueue_time'] == job.get_enqueue_time().isoformat()
    assert response['creator'] == job.get_user().get_username()
    assert response['status'] == job.get_status().name

    # ------4-------
    request = {
        "user": "jobuser1",
        "job_id": job3_id
    }

    json_string = json.dumps(request)
    with pytest.raises(NoProjectManagerRightsException):
        app.get_job(json_string)

    # ------5-------
    request = {
        "user": "jobuser1",
        "job_id": job1_id
    }

    json_string = json.dumps(request)
    with pytest.raises(NoProjectManagerRightsException):
        app.get_job(json_string)
