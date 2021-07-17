import pytest
import json
import datetime

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
def test_get_queue():
    """
    /SA310/
    """
    jobs = Job.get_jobs(None, [JobStatus.QUEUED])
    for current_job in jobs:
        current_job.set_status(JobStatus.DONE)
    assert len(Job.get_jobs(None, [JobStatus.QUEUED])) == 0

    timestamp = datetime.datetime.now()

    try:
        admin = User.get_user_by_username("queueadmin1")
    except UserNotFoundException:
        admin = Administrator("queueadmin1", "token")

    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], admin)
    job1_id = job1.get_job_id()
    job1.set_status(JobStatus.QUEUED)
    job1.set_enqueue_time(timestamp)
    job1.set_priority(1)

    try:
        user = User.get_user_by_username("queueuser1")
    except UserNotFoundException:
        user = Administrator("queueuser1", "token")

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job2_id = job2.get_job_id()
    job2.set_status(JobStatus.QUEUED)
    job2.set_enqueue_time(timestamp)
    job2.set_priority(2)

    job3 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job3_id = job3.get_job_id()
    job3.set_status(JobStatus.QUEUED)
    job3.set_enqueue_time(timestamp)
    job3.set_priority(3)

    response = json.loads(app.get_queue())
    assert len(response) == 3
    for job_json in response:
        job = Job.get_job_by_id(job_json['job_id'])
        assert job_json['job_id'] == job1_id or job_json['job_id'] == job2_id or job_json['job_id'] == job3_id
        assert job_json['job_id'] == job.get_job_id()
        assert job_json['source'] == job.get_source_alias() + ":" + job.get_source_relative_path()
        assert job_json['enqueue_time'] == job.get_enqueue_time().isoformat()
        assert job_json['creator'] == job.get_user().get_username()
        assert job_json['priority'] == job.get_priority()
        assert job_json['status'] == job.get_status().name

