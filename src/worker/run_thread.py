#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time

from worker.task import Task
from worker.task_status import TaskStatus
from worker.worker_status import WorkerStatus
from worker.worker_class import Worker
from worker.msg_out import Out


class RunThread(threading.Thread):
    """The thread executing the template method."""

    def __init__(self, task: Task, worker: Worker, msg_out: Out):
        """The constructor.
        
        :param task: the initialized Task.
        :param worker: the worker class
        :param msg_out: the class for outgoing messages"""
        self._task = task
        self._worker = worker
        self._msg = msg_out
        # initialize thread
        threading.Thread.__init__(self)

    def run(self, ):
        self.evaluate_and_run_task()

    def evaluate_and_run_task(self):
        """
        Decides what to do next based on task.get_status.
        In fact this implements the result driven algorithm for the move command:
        First executes copy method, then consistency check, then delete.
        Updates the Master after each step via msg_out.
        If TaskStatus is set to either exception or error, pauses the worker and sends detailed report
        to Master via msg_out.
        If TaskStatus is set to terminated, sends detailed report and stops execution of task.
        """
        # we just notify here instead of in all the methods. but we have to skip this at busy wait...
        stat = self._task.status
        if stat == TaskStatus.COPYING:
            wait_cnt = 0
            # We could enter deadlock here, so we circumvent this with a watchdog counter
            # ALso, signaling Master every time would be too much... so we check this before updating.
            # wait for 60 seconds to see if status was changed in that time
            time.sleep(60000)
            wait_cnt += 1
            # we wait for one hour maximum
            if wait_cnt < 60:
                self.evaluate_and_run_task()
            return
        # update task and then decide what to do next
        self._msg.update_task(self._task)
        if stat == TaskStatus.INITIALIZED:
            self._task = self._worker.copy(self._task)
            self.evaluate_and_run_task()
        elif stat == TaskStatus.COPIED:
            self._task = self._worker._consistency_check(self._task)
            self.evaluate_and_run_task()
        elif stat == TaskStatus.CHECKED:
            self._task = self._worker.delete(self._task)
            self.evaluate_and_run_task()
        elif stat == TaskStatus.DELETED:
            # at the moment we do not do anything else here, but one could insert another step if needed
            self._task.status = TaskStatus.FINISHED
            self._worker.status = WorkerStatus.WAITING
            self._task = None
        elif stat == TaskStatus.PAUSED:
            # we do not busy wait here as we want to wait for a resume_paused_task command
            return
        elif stat == TaskStatus.TERMINATED:
            self._msg.update_task(self._task)
            self._task = None
        elif stat == TaskStatus.ERROR:
            # at error we pause and wait for resume_paused_task command
            self._msg.raise_error(self._task)
            self._worker.status = WorkerStatus.PAUSED
        elif stat == TaskStatus.EXCEPTION:
            # at error we pause and wait for resume_paused_task command
            self._msg.raise_exception(self._task)
            self._worker.status = WorkerStatus.PAUSED
        return
