#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from exceptions.no_active_task_exception import NoActiveTaskException
from worker.action import Action
from worker.task import Task
from worker.task_status import TaskStatus
from worker.run_thread import RunThread

from exceptions.naming_convention_error import NamingConventionError
from exceptions.storage_alias_not_found_exception import StorageAliasNotFoundException
from exceptions.storage_not_mounted_exception import StorageNotMountedException
from exceptions.worker_status_exception import WorkerStatusException
from worker.tool_config_parser import ToolConfigParser
from worker.worker_status import WorkerStatus


class MsgIn:
    """
    The facade of worker.
    Accepts commands from master and callst the suiting handling routine in worker.
    """

    def __init__(self, token, worker_address, msg_out, worker, task=None):
        """The Constructor. 
        WARNING: call only if msg_out is already registered.
        """
        self._authentification_token = token
        self._worker_address = worker_address
        self._msg = msg_out
        self._worker = worker
        self._task = task
        self._wait_cnt = 0
        self._thread = None
        if task is not None:
            # WARNING wait for register!
            msg_out.update_status(WorkerStatus.ACTIVE)
            self.resume_paused_task()

    def assign_task(self, user_name, job_id, source_path, target_path, copy_options):
        """
        Checks an incoming move command for validity.
        If the command is accepted, returns ok and iniciates the move process.
        ELse returns suiting error code.
        """
        try:
            action = Action(copy_options['action'])
            executable = ToolConfigParser().get_executable_path(copy_options['copytool'])
            copytool_class = ToolConfigParser().get_copytool_class(copy_options['copytool'])


            copytool = copytool_class(copy_options['retrycount'], copy_options['options'], executable)
            new_task = Task(job_id, source_path, self._msg, target_path=target_path,
                            copytool=copytool, action=action)
            self._task = self._worker.adopt_task(new_task)
        except StorageAliasNotFoundException as e:
            self._task.add_exception(e)
            self._task.status = TaskStatus.EXCEPTION
            self._msg.raise_exception(self._task)
            return {
                'Exception': 'StorageAliasNotFoundException',
            }
        except StorageNotMountedException as e:
            self._task.add_exception(e)
            self._task.status = TaskStatus.EXCEPTION
            self._msg.raise_exception(self._task)
            return {
                'Exception': 'StorageNotMountedException',
            }
        except WorkerStatusException as e:
            return {
                'Exception': 'WorkerStatusException',
            }
        except NamingConventionError as e:
            return {
                'Exception': 'NamingConventionError',
            }
        self._thread = RunThread(self._task, self._worker, self._msg)
        self._thread.start()
        return {
            'Exception': 'None',
        }

    def cancel_task(self, ):
        """
        Cancels the currently running task.
        Kills the copytool subprocess, then deletes already transfered files in target storage.
        Sets WorkerStatus to waiting and exits.
        """
        if self._task is None:
            return {
                'Exception': 'NoTaskException',
            }
        try:
            task = self._worker.cancel_task(self._task)
        except WorkerStatusException as stat:
            return {
                'Exception': 'WorkerStatusException',
            }
        except NoActiveTaskException as e:
            return {
                'Exception': 'NoActiveTaskException'
            }
        # we do not worry about not existing tasks, because we would have returned before
        if task.status == TaskStatus.ERROR:
            self._msg.raise_error(task)
        elif task.status == TaskStatus.EXCEPTION:
            self._msg.raise_exception(task)

    def resume_paused_task(self, ):
        """
        Continues a previously paused task at its execution point.
        If TaskStatus was exception or error, restarts the task.
        """
        if self._task is None:
            return {
                'Exception': 'NoTaskException',
            }
        try:
            self._task = self._worker.resume_paused_task(self._task)
        except WorkerStatusException as e:
            return {
                'Exception': 'WorkerStatusException',
            }
        self._thread = RunThread(self._task, self._worker, self._msg)
        self._thread.start()
        self._evaluate_task_stat()

    def get_status(self, ):
        """Getter for WorkerStatus."""
        return self._worker.status.name

    def get_worker_name(self, ):
        """Getter for WorkerName"""
        return self._worker.get_name()

    def deactivate_worker(self, ):
        """
        Deactivates worker after canceling running task.
        A deactivated worker does not accept any incoming requests.
        """
        self._task = self._worker.deactivate_worker(self._task)
        # update task status and delete it. Carefull, it may be None
        if self._task:
            self._msg.update_task(self._task)
            self._task = None
        self._thread = None
        return {}

    def activate_worker(self):
        """
        If status was deactivated before, changes to waiting and returns True,
        else does nothing and returns False.
        """
        return self._worker.activate_worker()
