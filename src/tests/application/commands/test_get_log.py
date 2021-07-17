import pytest
import json
import datetime

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
def test_get_log():
    """
    1. Admin requests logs of user. /SA210/
    2. User requests his own logs /SA220/
    3. Another user(not admin) requests logs of user /SA230/
    :return:
    """
    try:
        user1 = User.get_user_by_username("loguser1")
        jobs = Job.get_jobs([user1.get_username()], [JobStatus.PAUSED, JobStatus.QUEUED,
                                                     JobStatus.ACTIVE, JobStatus.DONE])
        for current_job in jobs:
            current_job.set_status(JobStatus.ACTIVE)
    except UserNotFoundException:
        user1 = User("loguser1", "token")

    timestamp = datetime.datetime.now()

    active_job_ids_user1 = []
    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1.set_status(JobStatus.DONE)
    job1.set_start_time(timestamp)
    job1.set_end_time(timestamp)
    job1.set_enqueue_time(timestamp)
    active_job_ids_user1.append(job1.get_job_id())

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job2.set_status(JobStatus.DONE)
    job2.set_start_time(timestamp)
    job2.set_end_time(timestamp)
    job2.set_enqueue_time(timestamp)

    active_job_ids_user1.append(job2.get_job_id())
    job3 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job3.set_status(JobStatus.DONE)
    job3.set_start_time(timestamp)
    job3.set_end_time(timestamp)
    job3.set_enqueue_time(timestamp)
    active_job_ids_user1.append(job3.get_job_id())

    # -----------1------------
    try:
        admin = User.get_user_by_username("logadmin1")
    except UserNotFoundException:
        admin = Administrator("logadmin1", "token")

    request = {
        "days": "5",
        "user": "logadmin1",
        "for_user": "loguser1"
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_log(json_string))

    assert len(response) == 3
    for job in response:
        assert job['job_id'] in active_job_ids_user1

    # -----------2------------
    request = {
        "days": "5",
        "user": "loguser1",
        "for_user": "loguser1"
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_log(json_string))

    assert len(response) == 3
    for job in response:
        assert job['job_id'] in active_job_ids_user1

    # -----------3------------
    try:
        false_admin = User.get_user_by_username("logadminfalse1")
    except UserNotFoundException:
        false_admin = User("logadminfalse1", "token")

    request = {
        "days": "5",
        "user": "logadminfalse1",
        "for_user": "loguser2"
    }

    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        app.get_log(json_string)


def test_get_log_different_days():
    """
    /SA240/
    """
    try:
        user1 = User.get_user_by_username("loguser2")
        jobs = Job.get_jobs([user1.get_username()], [JobStatus.PAUSED, JobStatus.QUEUED,
                                                     JobStatus.ACTIVE, JobStatus.DONE])
        for current_job in jobs:
            current_job.set_status(JobStatus.ACTIVE)
    except UserNotFoundException:
        user1 = User("loguser2", "token")

    timestamp = datetime.date.today() - datetime.timedelta(days=2)

    active_job_ids_user1 = []
    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1.set_status(JobStatus.DONE)
    job1.set_start_time(timestamp)
    job1.set_end_time(timestamp)
    job1.set_enqueue_time(timestamp)
    active_job_ids_user1.append(job1.get_job_id())

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job2.set_status(JobStatus.DONE)
    job2.set_start_time(timestamp)
    job2.set_end_time(timestamp)
    job2.set_enqueue_time(timestamp)

    active_job_ids_user1.append(job2.get_job_id())
    job3 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job3.set_status(JobStatus.DONE)
    job3.set_start_time(timestamp)
    job3.set_end_time(timestamp)
    job3.set_enqueue_time(timestamp)
    active_job_ids_user1.append(job3.get_job_id())

    # Log for last 3 days
    request = {
        "days": "3",
        "user": "loguser2",
        "for_user": "loguser2"
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_log(json_string))

    assert len(response) == 3
    for job in response:
        assert job['job_id'] in active_job_ids_user1

    # Log for last day
    request = {
        "days": "1",
        "user": "loguser2",
        "for_user": "loguser2"
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_log(json_string))

    assert len(response) == 0


def test_get_log_user_not_found():
    """
    /SA250/
    """
    request = {
        "days": "3",
        "user": "asdafadsfasfasfasdfdsfgjhsdfjkghkjr34443433443",
        "for_user": "fgjdslgjldsfkjglksdjfglkjsdlfkjgls34433434343dfjg"
    }

    json_string = json.dumps(request)
    with pytest.raises(UserNotFoundException):
        app.get_log(json_string)
