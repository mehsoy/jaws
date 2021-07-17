import pytest
import datetime
import json

from application.system.job import Job, JobStatus
from application.system.user import User
from application.system.user_role import UserRole
from application.handlers.response_builder import ResponseBuilder
from exceptions.user_not_found_exception import UserNotFoundException

rb = ResponseBuilder()


def test_build_create_job():
    expected_answer = '{"job_id": 1}'
    assert rb.build_create_job(1) == expected_answer
    return


def test_build_log():
    try:
        user = User.get_user_by_username("rbuser")
    except UserNotFoundException:
        user = User("rbuser", "token")

    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job1_id = job1.get_job_id()
    job1.set_status(JobStatus.DONE)
    timestamp = datetime.datetime.now()
    job1.set_enqueue_time(timestamp)
    job1.set_end_time(timestamp)

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job2_id = job2.get_job_id()
    job2.set_status(JobStatus.DONE)
    timestamp = datetime.datetime.now()
    job2.set_enqueue_time(timestamp)
    job2.set_end_time(timestamp)

    job1 = Job.get_job_by_id(job1_id)
    job2 = Job.get_job_by_id(job2_id)
    answer = json.loads(rb.build_log([job1, job2]))

    job1 = Job.get_job_by_id(job1_id)
    assert answer[0]["job_id"] == job1.get_job_id()
    assert answer[0]["source"] == job1.get_source_alias() + ":" + job1.get_source_relative_path()
    assert answer[0]["target"] == job1.get_target_alias()
    assert answer[0]["enqueue_time"] == job1.get_enqueue_time().isoformat()
    assert answer[0]["end_time"] == job1.get_end_time().isoformat()
    assert answer[0]["creator"] == job1.get_user().get_username()
    assert answer[0]["status"] == job1.get_status().name
    assert answer[0]["error"] == job1.get_error()

    job2 = Job.get_job_by_id(job2_id)
    assert answer[1]["job_id"] == job2.get_job_id()
    assert answer[1]["source"] == job2.get_source_alias() + ":" + job2.get_source_relative_path()
    assert answer[1]["target"] == job2.get_target_alias()
    assert answer[1]["enqueue_time"] == job2.get_enqueue_time().isoformat()
    assert answer[1]["end_time"] == job2.get_end_time().isoformat()
    assert answer[1]["creator"] == job2.get_user().get_username()
    assert answer[1]["status"] == job2.get_status().name
    assert answer[1]["error"] == job2.get_error()


def test_build_running():
    try:
        user = User.get_user_by_username("rbuser1")
    except UserNotFoundException:
        user = User("rbuser1", "token")

    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job1_id = job1.get_job_id()
    job1.set_status(JobStatus.DONE)
    timestamp = datetime.datetime.now()
    job1.set_enqueue_time(timestamp)
    job1.set_end_time(timestamp)

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job2_id = job2.get_job_id()
    job2.set_status(JobStatus.DONE)
    timestamp = datetime.datetime.now()
    job2.set_enqueue_time(timestamp)
    job2.set_end_time(timestamp)

    job1 = Job.get_job_by_id(job1_id)
    job2 = Job.get_job_by_id(job2_id)
    answer = json.loads(rb.build_active([job1, job2]))

    job1 = Job.get_job_by_id(job1_id)
    assert answer[0]["job_id"] == job1.get_job_id()
    assert answer[0]["source"] == job1.get_source_alias() + ":" + job1.get_source_relative_path()
    assert answer[0]["target"] == job1.get_target_alias()
    assert answer[0]["enqueue_time"] == job1.get_enqueue_time().isoformat()
    assert answer[0]["creator"] == job1.get_user().get_username()
    assert answer[0]["status"] == job1.get_status().name

    job2 = Job.get_job_by_id(job2_id)
    assert answer[1]["job_id"] == job2.get_job_id()
    assert answer[1]["source"] == job2.get_source_alias() + ":" + job2.get_source_relative_path()
    assert answer[1]["target"] == job2.get_target_alias()
    assert answer[1]["enqueue_time"] == job2.get_enqueue_time().isoformat()
    assert answer[1]["creator"] == job2.get_user().get_username()
    assert answer[1]["status"] == job2.get_status().name


def test_build_directory_list():
    pass


def test_build_target_list():
    expected_answer = '{"targets": ["storage1", "storage2", "storage3"]}'
    assert rb.build_target_list(["storage1", "storage2", "storage3"]) == expected_answer
    return


def test_build_job():
    try:
        user = User.get_user_by_username("rbuser")
    except UserNotFoundException:
        user = User("rbuser", "token")
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job.set_status(JobStatus.QUEUED)
    timestamp = datetime.datetime.now()
    job.set_enqueue_time(timestamp)

    answer = json.loads(rb.build_job(job))
    assert answer["job_id"] == job.get_job_id()
    assert answer["source"] == job.get_source_alias() + ":" + job.get_source_relative_path()
    assert answer["target"] == job.get_target_alias()
    assert answer["enqueue_time"] == job.get_enqueue_time().isoformat()
    assert answer["creator"] == job.get_user().get_username()
    assert answer["status"] == job.get_status().name
    return


def test_build_team_list():
    pass


def test_build_queue():
    try:
        user = User.get_user_by_username("rbuser2")
    except UserNotFoundException:
        user = User("rbuser2", "token")

    job1 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job1_id = job1.get_job_id()
    job1.set_status(JobStatus.DONE)
    timestamp = datetime.datetime.now()
    job1.set_enqueue_time(timestamp)
    job1.set_end_time(timestamp)

    job2 = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job2_id = job2.get_job_id()
    job2.set_status(JobStatus.DONE)
    timestamp = datetime.datetime.now()
    job2.set_enqueue_time(timestamp)
    job2.set_end_time(timestamp)

    job1 = Job.get_job_by_id(job1_id)
    job2 = Job.get_job_by_id(job2_id)
    answer = json.loads(rb.build_queue([job1, job2]))

    job1 = Job.get_job_by_id(job1_id)
    assert answer[0]["job_id"] == job1.get_job_id()
    assert answer[0]["source"] == job1.get_source_alias() + ":" + job1.get_source_relative_path()
    assert answer[0]["target"] == job1.get_target_alias()
    assert answer[0]["enqueue_time"] == job1.get_enqueue_time().isoformat()
    assert answer[0]["creator"] == job1.get_user().get_username()
    assert answer[0]["priority"] == job1.get_priority()
    assert answer[0]["status"] == job1.get_status().name

    job2 = Job.get_job_by_id(job2_id)
    assert answer[1]["job_id"] == job2.get_job_id()
    assert answer[1]["source"] == job2.get_source_alias() + ":" + job2.get_source_relative_path()
    assert answer[1]["target"] == job2.get_target_alias()
    assert answer[1]["enqueue_time"] == job2.get_enqueue_time().isoformat()
    assert answer[1]["creator"] == job2.get_user().get_username()
    assert answer[1]["priority"] == job2.get_priority()
    assert answer[1]["status"] == job2.get_status().name


def test_build_workers():
    pass


def test_build_user_role():
    expected_answer = '{"role": "Administrator"}'
    assert rb.build_user_role(UserRole.Administrator) == expected_answer
    expected_answer = '{"role": "ProjectManager"}'
    assert rb.build_user_role(UserRole.ProjectManager) == expected_answer
    expected_answer = '{"role": "User"}'
    assert rb.build_user_role(UserRole.User) == expected_answer
    return


def test_build_exception():
    pass
