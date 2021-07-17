import pytest

from application.handlers.notification_handler import NotificationHandler
from application.system.job import Job, JobStatus
from application.system.user import User
from exceptions.user_not_found_exception import UserNotFoundException

notification_handler = NotificationHandler()


def test_active_job():
    try:
        user = User.get_user_by_username("uyefv")
    except UserNotFoundException:
        user = User("uyefv", "token")
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job.set_status(JobStatus.ACTIVE)
    notification_handler.resolve_notification(job)


def test_paused_job():
    try:
        user = User.get_user_by_username("uyefv")
    except UserNotFoundException:
        user = User("uyefv", "token")
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job.set_status(JobStatus.PAUSED)
    notification_handler.resolve_notification(job)


def test_done_job():
    try:
        user = User.get_user_by_username("uyefv")
    except UserNotFoundException:
        user = User("uyefv", "token")
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
    job.set_status(JobStatus.DONE)
    notification_handler.resolve_notification(job)

def test_error_job():
    try:
        user = User.get_user_by_username("uyefv")
    except UserNotFoundException:
        user = User("uyefv", "token")
    job = Job('storageA', 'storageB', '~/.data/', [False, False, False], user)
    job.set_error("Target not mounted")
    job.set_status(JobStatus.PAUSED)
    notification_handler.resolve_notification(job)
