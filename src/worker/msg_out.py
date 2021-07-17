#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from threading import Lock
from enum import Enum
import requests

from helpers import send_request
from worker.task import Task

from exceptions.worker_name_already_taken_error import WorkerNameAlreadyTakenError
from exceptions.connection_exception import ConnectionException
from exceptions.synchronization_exception import SynchronizationException


class Out:
    """
    The class notifying the master about every change in task status and possible errors.
    All methods are syncronized to make sure only one message at a time is sent.
    """
    BLOCK_TIMEOUT = "At worker '%s', in msg_out: Failed to acquire msg_lock due timeout."
    WRONG_NAME = ("The name '%s' is already used for another worker in the system. "
                  + "Please change it in the configuration file")

    def __init__(self, address, token, timeout: int, frequency: int):
        """The constructor of the class.
        
        :param address: The url used to communicate with master
        :param token: the token to identify the request in Master. Has to be sent with each request.
        :param timeout: the time in ms how long to try reconnect at connection loss
        :param frequency: the frequency to try reconnecting during connection loss
        """
        self._msg_lock = Lock()
        # the timeout (in seconds) to be used for lock.acquire(), must be a bit higher due send time
        self._lock_timeout = 10.0
        self._master_address = address
        self._authentification_token = token
        self._reconnect_timeout = timeout
        self._reconnect_frequency = frequency
        self._id = None

    def send_task_stats(self, task_id, stats):
        if not stats:
            # This means the copytool doesn't support this feature
            return
        url = self._master_address + '/jobs/' + str(task_id) + '/stats'
        self._send_to_master(data_out=stats, method='POST', url=url)

    def update_status(self, new_status: Enum):
        """Notifys master about new WorkerStatus.
        
        :param new_status: the new worker_status
        """
        if self._msg_lock.acquire(timeout=self._lock_timeout):
            self._send_to_master({'status': new_status.name}, 'PATCH', self._master_address +
                                 '/workers/' + self._id)
            self._msg_lock.release()
        else:
            raise (SynchronizationException(SynchronizationException(Out.BLOCK_TIMEOUT % self._id)))

    def update_task(self, task):
        """Notifys master about new TaskStatus. Retrieves all the informations from task and sends them.
        
        :param task: the task
        """
        if self._msg_lock.acquire(timeout=self._lock_timeout):
            taskvalues = self._retrieve_task_values(task)
            self._send_to_master(taskvalues, 'PATCH',
                                 self._master_address + '/jobs/' + str(taskvalues['id']))
            self._msg_lock.release()
        else:
            raise (SynchronizationException(Out.BLOCK_TIMEOUT % task.get_worker_name()))

    def register(self, master_adress, authentification_token, worker_name, worker_address, aliases, status):
        """Registers Worker at Master. 
        If a NoConnectionResponseException occurs retries to connect automatically. 
        If there was no successful connection after that a ConnectionError is raised.
        
        :raises ConnectionError: if connection attempt to master failed
        :raises WorkerNameAlreadyTakenError: from WorkerNameAlreadyTakenException in Master
        """
        data = {
            'worker_name': worker_name,
            'address': worker_address,
            'status': status.name,
            'mountpoints': aliases
        }
        response = self._send_to_master(data, 'POST', self._master_address + '/workers/')
        if response is not None and 'Exception' in response:
            raise WorkerNameAlreadyTakenError(Out.WRONG_NAME % worker_name)
        self._id = worker_name

    def raise_exception(self, task):
        """Notifies Master about an occured Exception in task.
        Retrieves Information from task and sends it to Master.
        
        :param task: the task containing the information
        """
        if self._msg_lock.acquire(timeout=self._lock_timeout):
            taskvalues = dict()
            taskvalues["exceptions"] = list(str(e) for e in task.get_exceptions())
            taskvalues = self._retrieve_task_values(task, taskvalues)
            self._send_to_master(taskvalues, 'PATCH',
                                 self._master_address + '/jobs/' + str(taskvalues['id']))
            self._msg_lock.release()
        else:
            raise (SynchronizationException(Out.BLOCK_TIMEOUT % task.get_worker_name()))

    def raise_error(self, task):
        """Notifies Master about an occured Error in task.
        Retrieves Information from task and sends it to Master.
        
        :param task: the task containing the information
        """
        if self._msg_lock.acquire(timeout=self._lock_timeout):
            taskvalues = dict()
            taskvalues["errors"] = list(str(err) for err in task.get_errors())
            taskvalues = self._retrieve_task_values(task, taskvalues)
            self._send_to_master(taskvalues, 'PATCH',
                                 self._master_address + '/jobs/' + str(taskvalues['id']))
            self._msg_lock.release()
        else:
            raise (SynchronizationException(Out.BLOCK_TIMEOUT % task.get_worker_name()))

    def _retrieve_task_values(self, task: Task, taskvalues=dict()):
        """Reads all the neccessary data from task."""
        taskvalues["worker_name"] = self._id
        taskvalues["id"] = task.get_id()
        taskvalues["status"] = task.status.name
        taskvalues["absolute_target_path"] = task.absolute_target_path
        if task.get_starting_time() is not None:
            taskvalues["start_time"] = task.get_starting_time().isoformat()
        else:
            taskvalues["start_time"] = None
        if task.get_completion_time() is not None:
            taskvalues["completion_time"] = task.get_completion_time().isoformat()
        else:
            taskvalues["completion_time"] = None
        return taskvalues

    def _send_to_master(self, data_out, method, url):
        cookie = {'token': self._authentification_token}
        answer, text = send_request(method, url, cookies=cookie, json=data_out)
        if answer.status_code == 401:
            raise ConnectionException('Connection not authorized, make sure you used the correct token')
        if 'Exception' in answer:
            raise answer['Exception']
