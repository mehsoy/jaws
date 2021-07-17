#!/usr/bin/python
#-*- coding: utf-8 -*-
from application.search import search_class
from application.system.job import Job
from application.system.job_status import JobStatus
from .config_handler import ConfigHandler
from application.system.user import User, Administrator
from application.system.user_role import UserRole
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.permission_exception import PermissionException
from exceptions.semantic_exception import SemanticException
from exceptions.no_project_manager_rights_exception import NoProjectManagerRightsException
from exceptions.no_administrator_rights_exception import NoAdministratorRightsException


class AccessHandler:
    """
    Handler that checks the semantic of requests.

    """
    def __init__(self):
        self._config_handler = ConfigHandler()

    def check_create_job(self, job, calling_user):
        """
        Checks permissions for job creation. Checks:
        1) If calling_user can create job for for_user
        2) If user did not exceed the allowed amount of jobs
        :param job: job to be checked
        """
        if job.get_user().get_username() != calling_user.get_username():
            if calling_user.get_user_type() != UserRole.Administrator:
                raise NoAdministratorRightsException(calling_user.get_username() + " doesn't have "
                                                    "rights to create job for " + job.get_user().get_username())

        allowed_jobs_number = self._config_handler.get_max_tasks_number_for_user()
        if len(Job.get_jobs([job.get_user().get_username()],
                            [JobStatus.ACTIVE, JobStatus.QUEUED, JobStatus.PAUSED])) \
                > allowed_jobs_number:
            raise PermissionException(
                "Max. number of jobs (" + str(allowed_jobs_number) + ") for user "
                + job.get_user().get_username() + " exceeded")
        return

    def check_cancel_job(self, job, calling_user):
        """
        Checks permissions for job cancellation. Checks:
        1) If creator of job is calling_user or calling_user is admin
        2) If job is already done or cancelled
        :param job: job to be cancelled
        :param calling_user: initiates request
        """
        user = job.get_user()
        if user.get_username() != calling_user.get_username():
            if calling_user.get_user_type() != UserRole.Administrator:
                raise PermissionException(calling_user.get_username() + " is not permitted to cancel job "
                                          + str(job.get_job_id()))
        if job.get_status() in [JobStatus.DONE, JobStatus.CANCELED]:
            raise SemanticException("Job " + str(job.get_job_id()) + " is already done or cancelled")
        return

    def check_read_rights(self, for_user, calling_user):
        """
        Checks if calling_user can read information about jobs of for_user.
        :param for_user: has a job
        :param calling_user: accesses to this job
        """
        if for_user is None:
            if calling_user is not None:
                #When Projectmanager wants to see jobs(directories) of all his team members
                if calling_user.get_user_type() != UserRole.ProjectManager:
                    raise NoProjectManagerRightsException(calling_user.get_username()
                                                          + " is not project manager")
        else:
            if calling_user.get_user_type() != UserRole.Administrator:
                if calling_user.get_user_type() != UserRole.ProjectManager:
                    if calling_user.get_username() != for_user.get_username():
                        raise NoProjectManagerRightsException(calling_user.get_username()
                                                              + " has no access to jobs of " + for_user.get_username())
                else:
                    if not calling_user.has_user_in_team(for_user):
                        raise NoProjectManagerRightsException(calling_user.get_username()
                                                              + " is not a manager of " + for_user.get_username())
        return

    def check_write_rights(self, for_user, calling_user):
        pass

    def check_storage_access(self, storage_alias, calling_user):
        pass

    def check_set_rights(self, user, role):
        """
        Checks if user can have given role.
        Passes only ProjectManager role for now
        :param user: User
        :param role: UserRole
        """
        if user.get_user_type() == role:
            raise PermissionException(user.get_username() + " has already " + role.name + " role")
        return

    def check_set_priority(self, job):
        """
        Checks if priority can be set to the job
        :param job: Job
        """
        if job.get_status() not in [JobStatus.QUEUED]:
            raise PermissionException("Job " + str(job.get_job_id()) + " is not in the queue")
        return

    def check_add_user_to_team(self, user, manager):
        if manager.get_user_type() != UserRole.ProjectManager:
            raise SemanticException(manager.get_username() + " is not a project manager")
        """ Can project_manager be in another team as not project manager?"""
        if user.get_user_type() != UserRole.User:
            raise SemanticException("Can not add project manager or administrator" 
                                    + user.get_username() + " to the team")

        if manager.has_user_in_team(user):
            raise SemanticException(user.get_username() + " is already in a team of project manager"
                                    + manager.get_username())
        return

    def verify_user_via_token(self, username, token):
        """
        Verifies the identity of user. If user doesn't exist in the database, he will be created after
        given token will be compared with remote_token, that is stored by user.
        Given token is compared with database entry.
        :param username: user that has to be verified
        :param token: user credentials string
        :return: verified User
        """

        try:
            user = User.get_user_by_username(username)
        except UserNotFoundException:
            remote_token = search_class.get_user_credentials(username)
            if remote_token != token:
                return False
            if username in self._config_handler.get_administrators():
                user = Administrator(username, remote_token)
            else:
                user = User(username, remote_token)

        # In case a User was registered using munge a token is not present in the data base entry
        if not user.get_token():
            remote_token = search_class.get_user_credentials(username)
            user.set_token(remote_token)

        # Check if the token match
        if user.get_token() != token:
            # Update database entry in case credentials have changed
            remote_token = search_class.get_user_credentials(username)
            if remote_token != user.get_token():
                user.set_token(remote_token)
            if user.get_token() != token:
                return False

        return True

    def ensure_existance(self, username):
        try:
            User.get_user_by_username(username)
        except UserNotFoundException:
            if username in self._config_handler.get_administrators():
                Administrator(username)
            else:
                User(username)

    def check_resume(self, job):
        """
        Checks if job is paused
        :param job: to be checked
        :raise SemanticException
        """
        if job.get_status() != JobStatus.PAUSED:
            raise SemanticException("Job ID: " + str(job.get_job_id()) + " was not paused")
        return

