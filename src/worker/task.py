#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Lock

from exceptions.synchronization_exception import SynchronizationException
from worker.task_status import TaskStatus


# TODO this class is both data structure and an object, also violating SRP. Myb make
# TaskConstructor class?
class Task:
    """A container for all important information on a move-task in Worker."""
    BLOCK_TIMEOUT = "At worker '%s', task '%d': Failed to acquire task_lock due timeout."

    def __init__(self, task_id: int, source_path: str,
                msg_out, target_path: str = None, copytool=None,
                 action=None):
        # Attributes initialized by constructor
        self._id = task_id
        self.source_path = source_path
        self.msg_out = msg_out
        self.target_path = target_path

        self._action = action
        self._task_lock = Lock()
        # the timeout (in seconds) to be used for lock.acquire()
        self._lock_timeout = 5.0
        self._worker_name = ""
        self._retry_count = 0
        self._start_time = None
        self._end_time = None
        # syncronized; please use setter and getter always
        self._task_status = None
        self._consystency_checktool = None
        self._copytool = copytool
        self._special_copytool_options = None
        self._exceptions = []
        self._errors = []

    @property
    def action(self):
        return self._action

    @property
    def absolute_source_path(self, ):
        return self.source_path

    @property
    def absolute_target_path(self, ):
        return self.target_path

    @property
    def worker_name(self):
        return self._worker_name

    @worker_name.setter
    def worker_name(self, worker_id: str):
        self._worker_name = worker_id

    @property
    def status(self, ):
        """Getter for _task_status, using synchronization to keep status consistent.

        :raises SynchronizationException: if the timeout to aquire lock was exceeded.
        """
        if self._task_lock.acquire(timeout=self._lock_timeout):
            status = self._task_status
            self._task_lock.release()
            return status
        else:
            raise (SynchronizationException(Task.BLOCK_TIMEOUT % (self._worker_name, self._id)))

    @status.setter
    def status(self, new_status: TaskStatus):
        """Setter for _task_status, using synchronization to keep status consistent. 
        Does not averwrite error status.
        
        :param new_status: the status to be set to
        :raises SyncronizationException: if the timeout to aquire lock was exceeded.
        """
        if self._task_lock.acquire(timeout=self._lock_timeout):
            # never overwrite errors!
            if self._task_status == TaskStatus.ERROR or self._task_status == TaskStatus.EXCEPTION:
                self._task_lock.release()
                return
            else:
                self._task_status = new_status
                self._task_lock.release()
            self.msg_out.update_task(self)
        else:
            raise (SynchronizationException(Task.BLOCK_TIMEOUT % (self._worker_name, self._id)))

    def set_status_force(self, status):
        """Setter for _task_status, using synchronization to keep status consistent.
        Use with caution, error status may be overwritten.
        
        :param status: the status to be set to
        :raises SyncronizationException: if the timeout to aquire lock was exceeded.
        """
        if self._task_lock.acquire(timeout=self._lock_timeout):
            # no error check here
            self._task_status = status
            self._task_lock.release()
        else:
            raise (SynchronizationException(Task.BLOCK_TIMEOUT % (self._worker_name, self._id)))

    @property
    def copytool(self, ):
        return self._copytool

    @copytool.setter
    def copytool(self, tool):
        self._copytool = tool

    def set_special_tool_options(self, options):
        self._special_copytool_options = options

    def set_starting_time(self, start):
        self._start_time = start

    def set_completion_time(self, end):
        self._end_time = end

    def increment_retry(self, ):
        self._retry_count += 1

    def add_exception(self, exception):
        self._exceptions.append(exception)

    def add_error(self, error):
        self._errors.append(error)

    def get_id(self):
        return self._id

    def get_special_tool_options(self, ):
        return self._special_copytool_options

    def get_starting_time(self, ):
        return self._start_time

    def get_completion_time(self, ):
        return self._end_time

    def get_retry_count(self, ):
        return self._retry_count

    def get_exceptions(self, ):
        return self._exceptions

    def get_errors(self, ):
        return self._errors

