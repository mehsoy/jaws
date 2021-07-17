#!/usr/bin/python
# -*- coding: utf-8 -*-
from application.system.job import Job, JobStatus
from master.worker import Worker, WorkerStatus
from application.system.user import User
from exceptions.user_not_found_exception import UserNotFoundException


class Master:
    _instance = None

    def __init__(self, ):
        pass

    @classmethod
    def get_master(cls):
        if cls._instance is None:
            cls._instance = Master()
        return cls._instance

    def get_workers(self, ):
        workers = []
        worker1 = Worker('worker1', 'WAITING', None, '192.168.0.1:1234', ['storageA', 'storageB'])
        workers.append(worker1)

        try:
            user = User.get_user_by_username("workeruser1")
        except UserNotFoundException:
            user = User("workeruser1", "token")
        job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
        worker2 = Worker('worker2', 'ACTIVE', job.get_job_id(), '192.168.0.2:1234', None)
        workers.append(worker2)

        return workers

    def add_to_queue(self, job):
        return

    def set_priority(self, job, new_priority):
        job.set_priority(new_priority)
        return

    def cancel_job(self, job):
        job.set_status(JobStatus.CANCELED)

    def resume_job(self, job):
        return

    def disable_worker(self, worker):
        return

    def enable_worker(self, worker):
        return

    def enable(self, ):
        return

    def disable(self, ):
        return
