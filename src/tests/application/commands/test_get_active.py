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
def test_get_active():
    """
    1. Admin requests running jobs of user. /SA410/
    2. User requests his own running jobs /SA420/
    3. Another user(not admin) requests running jobs of user /SA430/
    :return:
    """
    try:
        user1 = User.get_user_by_username("runuser1")
        jobs = Job.get_jobs([user1.get_username()], [JobStatus.PAUSED, JobStatus.QUEUED,
                                                     JobStatus.ACTIVE, JobStatus.DONE])
        for current_job in jobs:
            current_job.set_status(JobStatus.DONE)
    except UserNotFoundException:
        user1 = User("runuser1", "token")

    timestamp = datetime.datetime.now()

    active_job_ids_user1 = []
    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1.set_status(JobStatus.ACTIVE)
    job1.set_start_time(timestamp)
    job1.set_enqueue_time(timestamp)
    active_job_ids_user1.append(job1.get_job_id())

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job2.set_status(JobStatus.QUEUED)
    job2.set_start_time(timestamp)
    job2.set_enqueue_time(timestamp)

    active_job_ids_user1.append(job2.get_job_id())
    job3 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job3.set_status(JobStatus.ACTIVE)
    job3.set_start_time(timestamp)
    job3.set_enqueue_time(timestamp)
    active_job_ids_user1.append(job3.get_job_id())

    # -----------1------------
    try:
        admin = User.get_user_by_username("runadmin1")
    except UserNotFoundException:
        admin = Administrator("runadmin1", "token")

    request = {
        "user": "runadmin1",
        "for_user": "runuser1"
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_active(json_string))

    assert len(response) == 3
    for job in response:
        assert job['job_id'] in active_job_ids_user1

    # -----------2------------
    request = {
        "user": "runuser1",
        "for_user": "runuser1"
    }

    json_string = json.dumps(request)
    response = json.loads(app.get_active(json_string))

    assert len(response) == 3
    for job in response:
        assert job['job_id'] in active_job_ids_user1

    # -----------3------------
    try:
        false_admin = User.get_user_by_username("runadminfalse1")
    except UserNotFoundException:
        false_admin = User("runadminfalse1", "token")

    request = {
        "user": "runadminfalse1",
        "for_user": "runuser1"
    }

    json_string = json.dumps(request)
    with pytest.raises(PermissionException):
        app.get_active(json_string)


def test_get_active_user_not_found():
    """
    /SA440/
    """
    request = {
        "user": "asdafadsfasfasfasdfdsfgjhsdfjkghkjr34443433443",
        "for_user": "fgjdslgjldsfkjglksdjfglkjsdlfkjgls34433434343dfjg"
    }

    json_string = json.dumps(request)
    with pytest.raises(UserNotFoundException):
        app.get_active(json_string)
