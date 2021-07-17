#!/usr/bin/python
#-*- coding: utf-8 -*-

import requests
from json import loads, dumps
from helpers import send_request

from exceptions.no_response_from_worker_exception import NoResponseFromWorkerException
from exceptions.connection_exception import ConnectionException
from exceptions.permission_exception import PermissionException

class WorkerCommunicator():
    _instance = None

    def __init__(self, token):
        """
        Default constructor
        :param token: authentification key of master
        :type token: String
        """
        self.token = token
        self.retrycount = 5

    @classmethod    
    def get_communicator(cls, token):
        """
        Used to create singleton
        :param token: authentification key of master
        :type token: String
        """
        if cls._instance is None:
            cls._instance = WorkerCommunicator(token)
        return cls._instance

    def change_status_worker(self, worker, status):
        url = worker.get_address() + '/workers/'  
        data = {
            'status': status
        } 
        
        self.call_url(url, None, data, 'PATCH')
        
    def change_status_job(self, worker, status):
        if status == 'CANCELED':
            url = worker.get_address() + '/task/'
            return self.call_url(url, None, None, 'DELETE')
        else:
            url = worker.get_address() + '/task/'
            data = {
                'status': status
            }

            return self.call_url(url, None, data, 'PUT')
     
    def assign_task(self, job, worker):
            url = worker.get_address() + '/task/'
            data = {
                'job_id': job.id,
                'source_path': job.source_path,
                'user_name': job.user,
                'target_path': job.target_path,
                'copy_options': loads(job.copy_options),
            }

            return self.call_url(url, None, data, 'POST')

    def get_status(self, worker):
            url = worker.get_address() + '/workers/'
            return self.call_url(url, None, None, 'GET')
     
    def call_url(self, url, header, data, verb):
        cookie = {'token': self.token}
        try:

            response, text = send_request(verb, url, headers=header, cookies=cookie, json=data)
        except requests.exceptions.ConnectionError:
           return {'Exception': 'ConnectionError'}
        if response.status_code == 401:
            raise ConnectionException('Connection not authorized, make sure you used the correct token')
        elif response.status_code == 500:
            raise ConnectionException('Internal Server Error in Worker')
        return text

    def handle_response_code(status):
        if status == 200 or status == 201:
            return
        elif status == 400 or status == 403 or status == 405:
            raise PermissionException(response_dict[status])
        elif status == 408:
            raise NoResponseFromWorkerException(response_dict[status])
        #elif status == 409:
            #raise WorkerBusyException(response_dict[status])
       # elif status == 500:
            #raise WorkerCrashedException(response_dict[staatus])

    response_dict = {
        200 : 'Ok',
        201 : 'Created',
        400 : 'Bad Request',
        401 : 'Unauthorized',
        403 : 'Forbidden',
        404 : 'Not Found',
        405 : 'Method Not Allowed',
        408 : 'Request Time-out',
        409 : 'Conflict',
        500 : 'Internal Server Error'
    }
