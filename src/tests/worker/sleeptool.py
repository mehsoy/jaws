#!/usr/bin/python
# -*- coding: utf-8 -*-
from threading import Lock

import subprocess

from worker.action import Action
from worker.copytool.copytool import Copytool
from worker.task import Task
from worker.task_status import TaskStatus


class SleeperCopytool(Copytool):
    """Mock object to test process killing"""

    @property
    def SUPPORTED_ACTIONS(self, ):
        return [Action.COPY]

    def consistency_check(self, task: Task):
        task.status = TaskStatus.CHECKED
        return task

    def delete(self, task: Task):
        task.status = TaskStatus.DELETED
        return task

    # def kill_process(self, task):
    #     """Description in Copytool."""
    #     print("terminating...")
    #     try:
    #         self._process.kill()
    #     except Exception as e:
    #         task.add_error(e)
    #         task.status = TaskStatus.ERROR
    #         self._process = None
    #         self._msg.raise_error(task)
    #         return task
    #     print("terminated!")
    #     self._process = None
    #     task.status = TaskStatus.TERMINATED
    #     return task
