import pytest
import datetime


from application.system.job import Job, JobStatus
from application.system.user import User
from exceptions.job_not_found_exception import JobNotFoundException
from exceptions.user_not_found_exception import UserNotFoundException

try:
    user = User.get_user_by_username("xyz")
except UserNotFoundException:
    user = User("xyz", "token")

@pytest.mark.order1
def test_constructor():

    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    #assert job.get_status() == JobStatus.QUEUED


def test_getters():
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    another_job = Job.get_job_by_id(job.get_job_id())
    assert another_job.get_job_id() == job.get_job_id()
    assert another_job.get_source_alias() == job.get_source_alias()
    assert another_job.get_target_alias() == job.get_target_alias()
    assert another_job.get_source_relative_path() == job.get_source_relative_path()
    assert another_job.get_start_time() == job.get_start_time()
    assert another_job.get_end_time() == job.get_end_time()
    assert another_job.get_enqueue_time() == job.get_enqueue_time()
    assert another_job.get_status() == job.get_status()
    assert another_job.has_start_notification() == job.has_start_notification()
    assert another_job.has_end_notification() == job.has_end_notification()
    assert another_job.has_error_notification() == job.has_error_notification()
    assert another_job.get_user().get_username() == job.get_user().get_username()


def test_setters():
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)

    timestamp = datetime.datetime.now()
    job.set_start_time(timestamp)
    job.set_end_time(timestamp)
    job.set_enqueue_time(timestamp)
    assert job.get_start_time() == timestamp
    assert job.get_end_time() == timestamp
    assert job.get_enqueue_time() == timestamp

    job.set_status(JobStatus.DONE)
    assert job.get_status() == JobStatus.DONE
    assert job.has_start_notification() == job.has_start_notification()
    assert job.has_end_notification() == job.has_end_notification()
    assert job.has_error_notification() == job.has_error_notification()


def test_get_jobs():
    #Build users and jobs
    try:
        user1 = User.get_user_by_username("user1")
        jobs = Job.get_jobs([user1.get_username()], [JobStatus.PAUSED, JobStatus.QUEUED,
                                                     JobStatus.ACTIVE, JobStatus.PAUSED])
        for current_job in jobs:
            current_job.set_status(JobStatus.DONE)
    except UserNotFoundException:
        user1 = User("user1", "token")

    try:
        user2 = User.get_user_by_username("user2")
        jobs = Job.get_jobs([user2.get_username()], [JobStatus.PAUSED, JobStatus.QUEUED,
                                                     JobStatus.ACTIVE, JobStatus.PAUSED])
        for current_job in jobs:
            current_job.set_status(JobStatus.DONE)
    except UserNotFoundException:
        user2 = User("user2", "token")

    try:
        user3 = User.get_user_by_username("user3")
        jobs = Job.get_jobs([user3.get_username()], [JobStatus.PAUSED, JobStatus.QUEUED,
                                                     JobStatus.ACTIVE, JobStatus.PAUSED])
        for current_job in jobs:
            current_job.set_status(JobStatus.DONE)
    except UserNotFoundException:
        user1 = User("user3", "token")

    active_job_ids_user1 = []
    job1_1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_1.set_status(JobStatus.ACTIVE)
    active_job_ids_user1.append(job1_1.get_job_id())
    job1_2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_2.set_status(JobStatus.ACTIVE)
    active_job_ids_user1.append(job1_2.get_job_id())
    job1_3 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_3.set_status(JobStatus.ACTIVE)
    active_job_ids_user1.append(job1_3.get_job_id())

    queued_job_ids_user1 = []
    job1_4 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_4.set_status(JobStatus.QUEUED)
    queued_job_ids_user1.append(job1_4.get_job_id())
    job1_5 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_5.set_status(JobStatus.QUEUED)
    queued_job_ids_user1.append(job1_5.get_job_id())
    job1_6 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_6.set_status(JobStatus.QUEUED)
    queued_job_ids_user1.append(job1_6.get_job_id())

    canceled_job_ids_user1 = []
    job1_7 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_7.set_status(JobStatus.CANCELED)
    canceled_job_ids_user1.append(job1_7.get_job_id())
    job1_8 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_8.set_status(JobStatus.CANCELED)
    canceled_job_ids_user1.append(job1_8.get_job_id())
    job1_9 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user1)
    job1_9.set_status(JobStatus.CANCELED)
    canceled_job_ids_user1.append(job1_9.get_job_id())

    active_jobs_user1 = active_job_ids_user1.copy()
    queued_jobs_user1 = queued_job_ids_user1.copy()
    canceled_jobs_user1 = canceled_job_ids_user1.copy()

    jobs = Job.get_jobs([user1.get_username()], [JobStatus.ACTIVE])
    assert len(jobs) == 3
    for job in jobs:
        if job.get_job_id() not in active_jobs_user1:
            assert 1 == 0
        else:
            assert 1 == 1
            active_jobs_user1.remove(job.get_job_id())
    assert active_jobs_user1 == []
    active_jobs_user1 = active_job_ids_user1.copy()

    jobs = Job.get_jobs([user1.get_username()], [JobStatus.ACTIVE, JobStatus.QUEUED])
    assert len(jobs) == 6
    for job in jobs:
        if job.get_job_id() not in active_jobs_user1:
            if job.get_job_id() not in queued_jobs_user1:
                assert 1 == 0
            else:
                assert 1 == 1
                queued_jobs_user1.remove(job.get_job_id())
        else:
            assert 1 == 1
            active_jobs_user1.remove(job.get_job_id())
    assert active_jobs_user1 == []
    assert queued_jobs_user1 == []
    active_jobs_user1 = active_job_ids_user1.copy()
    queued_jobs_user1 = queued_job_ids_user1.copy()

    user2 = User.get_user_by_username("user2")
    active_job_ids_user2 = []
    job2_1 = Job('storageC', 'storageD', '~/.data/', [True, True, True], user2)
    job2_1.set_status(JobStatus.ACTIVE)
    active_job_ids_user2.append(job2_1.get_job_id())
    job2_2 = Job('storageC', 'storageD', '~/.data/', [True, True, True], user2)
    job2_2.set_status(JobStatus.ACTIVE)
    active_job_ids_user2.append(job2_2.get_job_id())
    job2_3 = Job('storageC', 'storageD', '~/.data/', [True, True, True], user2)
    job2_3.set_status(JobStatus.ACTIVE)
    active_job_ids_user2.append(job2_3.get_job_id())

    queued_job_ids_user2 = []
    job2_4 = Job('storageC', 'storageD', '~/.data/', [True, True, True], user2)
    job2_4.set_status(JobStatus.QUEUED)
    queued_job_ids_user2.append(job2_4.get_job_id())
    job2_5 = Job('storageC', 'storageD', '~/.data/', [True, True, True], user2)
    job2_5.set_status(JobStatus.QUEUED)
    queued_job_ids_user2.append(job2_5.get_job_id())
    job2_5 = Job('storageC', 'storageD', '~/.data/', [True, True, True], user2)
    job2_5.set_status(JobStatus.QUEUED)
    queued_job_ids_user2.append(job2_5.get_job_id())

    active_jobs_user2 = active_job_ids_user2.copy()
    queued_jobs_user2 = queued_job_ids_user2.copy()

    jobs = Job.get_jobs([user1.get_username(), user2.get_username()], [JobStatus.ACTIVE])
    assert len(jobs) == 6
    for job in jobs:
        if job.get_job_id() not in active_jobs_user1:
            if job.get_job_id() not in active_jobs_user2:
                assert 1 == 0
            else:
                assert 1 == 1
                active_jobs_user2.remove(job.get_job_id())
        else:
            assert 1 == 1
            active_jobs_user1.remove(job.get_job_id())
    assert active_jobs_user1 == []
    assert active_jobs_user2 == []
    active_jobs_user1 = active_job_ids_user1.copy()
    active_jobs_user2 = active_job_ids_user2.copy()

    job3 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user3)
    job3.set_status(JobStatus.PAUSED)
    time = datetime.datetime.now() - datetime.timedelta(days=10)
    job3.set_end_time(time)
    jobs = Job.get_jobs(None, [JobStatus.PAUSED], 8)
    assert len(jobs) == 0
    jobs = Job.get_jobs(None, [JobStatus.PAUSED], 12)
    assert len(jobs) == 1


def test_remove():
    job = Job('mystorage', 'storageB', '~/.data/', [True, True, True], user)
    job_id = job.id
    job_get = Job.get_job_by_id(job_id)
    assert job_get is not None
    job.remove()
    try:
        Job.get_job_by_id(job_id)
    except JobNotFoundException:
        assert 1 == 1
        return
    assert 0 == 0
