#!/usr/bin/python
#-*- coding: utf-8 -*-
from application.system.job import Job, JobStatus
from application.handlers.email_service import EmailService
from application.handlers.config_handler import ConfigHandler
import datetime


class NotificationHandler:
    """
    Handles notification, that have to be resolved with MessageService
    """
    MESSAGE = "\n\nAutomatically generated message from DMD\n" + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    _config_handler = ConfigHandler()

    def __init__(self):
        self._message_service = EmailService(self._config_handler.get_email_domain())

    def resolve_notification(self, job):
        """
        Resolves notification.
        :param job: Job with changed status
        """
        job_id = "Task ID " + str(job.get_job_id())
        if job.get_status() == JobStatus.ACTIVE and job.has_start_notification():
            self._message_service.mail([job.get_user()], job_id + " has been started."
                                       + self.MESSAGE)
        if job.get_status() == JobStatus.DONE and job.has_end_notification():
            self._message_service.mail([job.get_user()], job_id + " has been completed."
                                       + self.MESSAGE)
        if job.get_status() == JobStatus.PAUSED and job.has_error_notification():
            self._message_service.mail([job.get_user()], job_id + " has been paused."
                                       + self.MESSAGE)
        if job.get_error() is not None and job.get_status() == JobStatus.PAUSED:
            error_emails = self._config_handler.get_emails_for_errors()
            self._message_service.mail(None, job_id + " has been paused because of following error: "
                                       + job.get_error(), error_emails)
        return

    def resolve_exception_notification(self, exception):
        """
        Resolves error notification
        :param exception: exception with message
        """
        self._message_service.send(None, "Exception occurred: " + exception.message
                                   + self.MESSAGE)
        return
