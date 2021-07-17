#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import queue
from datetime import datetime
from threading import Lock

from exceptions.copy_sequence_exception import CopySequenceException
from exceptions.no_active_task_exception import NoActiveTaskException
from exceptions.source_path_not_valid_exception import SourcePathNotValidException
from exceptions.storage_alias_not_found_exception import StorageAliasNotFoundException
from exceptions.storage_not_mounted_error import StorageNotMountedError
from exceptions.storage_not_mounted_exception import StorageNotMountedException
from exceptions.synchronization_exception import SynchronizationException
from exceptions.worker_status_exception import WorkerStatusException
from worker.copytool.copytool import Copytool
from worker.mountcheck_thread import MountcheckThread, is_mounted
from worker.msg_out import Out
from worker.task import Task
from worker.task_status import TaskStatus
from worker.worker_status import WorkerStatus


class Worker:
    # better declare error messages here to easily change them
    NO_MOUNT = "At worker '%s' in task '%d' the storage '%s' is not mounted."
    STORAGE_NOT_EXIST = "At worker '%s': A Storage with the alias '%s' is not registered."
    PROCESS_NOT_RUNNING = "At worker '%s': You cannot kill a process that is not running."
    NO_TASK = "At worker '%s': Task may not be None."
    TASK_NOT_PAUSED = "At worker '%s': You cannot resume a task that is not paused."
    BLOCK_TIMEOUT = "At worker '%s': Failed to acquire worker_lock due timeout."
    STATUS = "Worker '%s' status is: '%s', needed: '%s'"

    def __init__(self, worker_name: str, msg_out: Out, mountpoints,
                 status: WorkerStatus = WorkerStatus.WAITING):
        self._worker_lock = Lock()
        # the timeout (in seconds) to be used for lock.acquire()
        self._lock_timeout = 10.0
        self._name = worker_name
        self._msg = msg_out
        self.mountpoints = mountpoints
        # syncronized, always use setter and getter, it will make your life
        # easier...
        self._status = status
        # we handle resuming task in msg_in

    def adopt_task(self, task: Task):
        """
        Checks if a task with the given parameters can be executed by this
        worker.
        If everything is ok, TaskStatus is set to initialized
        If a storage is not responding or an alias is not found,
        the corresponding exception is added to task.
        
        :param task: the task to be checked
        :return task: the updated task.
        :raises: StorageAliasNotFoundException, StorageNotMountedException,
        NoActiveTaskException,
        WorkerStatusException, NamingConventionError.
        """
        if task is None:
            raise (NoActiveTaskException(Worker.NO_TASK % self._name))
        status = self.status
        if status == WorkerStatus.WAITING:
            self.verify_task_mountpoints(task)
            self.accept_task(task)
        elif status == WorkerStatus.ACTIVE:
            raise (WorkerStatusException("Worker " + self._name + " is already running."))
        elif status == WorkerStatus.DEACTIVATED:
            raise (WorkerStatusException("Worker " + self._name + " is deactivated."))
        else:
            raise (WorkerStatusException("Worker " + self._name + " is deactivated."))
        return task

    def accept_task(self, task):
        task.status = TaskStatus.INITIALIZED
        task.worker_name = self._name
        self.status = WorkerStatus.ACTIVE

    def verify_task_mountpoints(self, task):
        src_mount, tgt_mount = None, None
        for m in self.mountpoints:
            if task.absolute_source_path.startswith(m): src_mount = m
            if task.absolute_target_path.startswith(m): tgt_mount = m

        if src_mount and tgt_mount and (not is_mounted(src_mount) or not is_mounted(tgt_mount)):
            raise StorageNotMountedException(Worker.NO_MOUNT % self._name)

    def cancel_task(self, task):
        """
        Cancels execution of current task.
        If cancelling was successfull TaskStatus is set to terminated.
        If any error/exception occured it is added to task and TaskStatus is
        set to error/exception.
        
        :param task: the currently paused task
        :return task: the updated task.
        :raises: NoActiveTaskException, WorkerStatusException
        """
        status = self.status
        if status is not WorkerStatus.ACTIVE:
            raise WorkerStatusException(Worker.STATUS % (self._name, status.name, "ACTIVE"))
        if task is None:
            raise (NoActiveTaskException(Worker.NO_TASK % self._name))
        stat = task.status
        if stat == TaskStatus.INITIALIZED or stat == TaskStatus.COPYING:
            task = task.copytool.kill_process(task)
            self.status = WorkerStatus.WAITING
            task.status = TaskStatus.TERMINATED
            return task
        else:
            raise (NoActiveTaskException(Worker.PROCESS_NOT_RUNNING % self._name))

    def resume_paused_task(self, task):
        """
        Initiates restart of move process by setting its status to initialized.
        like this the running thread will just restart the move process.
        
        :param task: the currently paused task
        :return task: the updated task.
        :raises: NoActiveTaskException, WorkerStatusException
        """
        if task is None:
            raise (NoActiveTaskException(Worker.NO_TASK % self._name))
        status = task.get_status
        # most likely we will have started due previous error.
        if status == TaskStatus.ERROR or status == TaskStatus.INITIALIZED or \
                status == TaskStatus.PAUSED:
            # we just start allover again
            self.status = WorkerStatus.ACTIVE
            task.status = TaskStatus.INITIALIZED
            return task
        else:
            raise WorkerStatusException(Worker.TASK_NOT_PAUSED % self._name)

    @property
    def status(self):
        """
        Getter for _status, using synchronization to keep status consistent.

        :raises SynchronizationException: if the timeout to aquire lock was
        exceeded.
        """
        if self._worker_lock.acquire(timeout=self._lock_timeout):
            status = self._status
            self._worker_lock.release()
            return status
        else:
            raise (SynchronizationException(Worker.BLOCK_TIMEOUT % self._name))

    @status.setter
    def status(self, status: WorkerStatus):
        """
        Setter for _status, using synchronization to keep status consistent.
        
        :param status: the status to be set to
        :raises SynchronizationException: if the timeout to aquire lock was
        exceeded.
        """
        if self._worker_lock.acquire(timeout=self._lock_timeout):
            self._status = status
            self._msg.update_status(new_status=status)

            self._worker_lock.release()
        else:
            raise (SynchronizationException(Worker.BLOCK_TIMEOUT % self._name))

    def get_name(self, ):
        """Getter for _name."""
        return self._name

    def deactivate_worker(self, task: Task = None):
        """
        Deactivates worker after canceling running task in copytool.
        
        :param task: the currently executed task
        :return task: the updated task.
        :raises: NoActiveTaskException
        """
        if task is not None:
            try:
                task = self.cancel_task(task)
            except WorkerStatusException:
                # we can just ignore it because we don't care if it is
                # running or not
                pass
        self.status = WorkerStatus.DEACTIVATED
        return task

    def activate_worker(self, ):
        """
        If status was deactivated before, changes to waiting, else does nothing.
        
        :raises: SynchronizationException
        """
        if self.status == WorkerStatus.DEACTIVATED:
            self.status = WorkerStatus.WAITING
            return True
        return False

    def copy(self, task: Task):
        """
        :raises: NoActiveTaskException
        """
        if task is None:
            raise (NoActiveTaskException(Worker.NO_TASK % self._name))
        self.validate_task(task)
        task.set_starting_time(datetime.now())
        # as blocking files does not work, insert another method for assuring consistency in source_file here

        stats = task.copytool.copy(task)
        self._msg.send_task_stats(task_id=task.get_id(), stats=stats)

        return task

    @staticmethod
    def validate_task(task):
        if not os.path.isdir(task.absolute_source_path):
            task.add_exception(SourcePathNotValidException(Copytool.INVALID_SOURCE
                                                           % (task.get_id(), task.absolute_source_path)))
            task.status = TaskStatus.EXCEPTION
            return task

    def _consistency_check(self, task):
        """
        Executes consistency check in Copytool
        
        :raises: NoActiveTaskException
        """
        if task is None:
            raise (NoActiveTaskException(Worker.NO_TASK % self._name))
        return task.copytool.consistency_check(task)

    def delete(self, task):
        """
        Calls copytool.delete() and updates task status on success.
        
        :param task: the currently executed task.
        :return task: the updated task.
        :raises: NoActiveTaskException
        """
        if task is None:
            raise (NoActiveTaskException(Worker.NO_TASK % self._name))
        if not task.status == TaskStatus.CHECKED:
            raise (CopySequenceException(Copytool.INVALID_OP % self.get_name()))

        task = task.copytool.delete(task)
        task.status = TaskStatus.DELETED
        task.set_completion_time(datetime.now())
        return task
