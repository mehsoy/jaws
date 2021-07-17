#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime

import dateutil.parser

from application.handlers.notification_handler import NotificationHandler
from application.system.job import Job
from application.system.job_status import JobStatus
from application.system.storage import Storage
from application.system.workspaces import Workspaces
from exceptions.master_paused_exception import MasterPausedException
from master.worker import Worker
from .master_communicator import WorkerCommunicator
from .worker_status import WorkerStatus

notification_handler = NotificationHandler()

class Master():
    """
    The main class to handle the queue
    implemented as a singleton
    """
    _instance = None
    _max_priority = None
    _token = 'secret01'
    _is_active = True
    
    def __init__(self, token=None, active=True, mailbox=None):
       
        """
        The Constructor. Warning: can break singleton if not used carefully
        """
        if token is not None:
            self._token = token
        if active is not None:
            self._is_active = active


        self._master_communicator = WorkerCommunicator(self._token)
        workers = Worker.get_all_workers()
        if Job.get_job_highest_priority() is not None:
            self._max_priority = Job.get_job_highest_priority().get_priority()
        else:
            self._max_priority = 0
        for worker in workers:
            status = self._master_communicator.get_status(worker)
            if 'Exception' in status:
                worker.delete()
            else:
                worker.set_status(status['status'])
                if worker.get_status() == WorkerStatus.WAITING and self._is_active:
                    job = self.look_for_work(worker)
                    if job is not None:
                        self.dequeue(job, worker)

    @classmethod
    def get_master(cls, token=None, mailbox=None):
        """
        This should be usesed as a constructor when using Master as a singleton
        """
        if cls._instance is None:
            cls._instance = Master(token=token, mailbox=mailbox)
        return cls._instance
    
    def get_workers(self,):
        """
        :returns: all workers
        """
        return Worker.get_all_workers()        
    
    def add_to_queue(self, job):
        """
        Adds a job to the queue
        :param job: the job to be added
        :type job: Job
        @raises MasterPausedException
        """
        if not self._is_active:
            raise MasterPausedException("The master is disabled, it will not accept new jobs")
        job.set_status('QUEUED')
        job.set_enqueue_time(datetime.datetime.now())
        job.set_priority(self._max_priority)
        usable = Worker.get_worker_by_storages(job.get_source_alias(), job.get_target_alias())
        if usable is not None:
            for worker in usable:
                if worker.get_status() == WorkerStatus.WAITING:
                    self.dequeue(job, worker)
                    #TODO return statement missing here?
        else:
            self._max_priority += 10

    def set_priority(self, job, new_priority):
        """
        Sets a new priority for the job
        :param job: the job to update
        :param new_priority: the new priority
        :type job: Job
        :type new_priority: integer
        """
        if Job.get_job_by_priority(new_priority):
            Job.get_job_by_priority(new_priority).set_priority(new_priority + 1)
        job.set_priority(new_priority)
        
    def cancel_job(self, job):
        """
        Cancels job that is either running or in queue
        :param job: Job to be cancelled
        :type job: Job
        @raises NoResponseFromWorkerException if the connection fails
        """
        if job.status == JobStatus.QUEUED:
            job.set_status(JobStatus.CANCELED)
            job.set_end_time(datetime.datetime.now())            
        elif job.status == JobStatus.ACTIVE:
            worker = Worker.get_worker_by_job_id(job.id)
            result = self._master_communicator.change_status_job(worker, 'CANCELED')
            if result and 'Exception' in result and result['Exception'] is not None:
                if result['Exception'] == 'NoTaskException' or result['Exception'] == 'NoActiveTaskException':
                    if job.get_status() == JobStatus.Done:
                        job.set_error('This Job was Canceled but already finished Copying, '
                                    'you can find your Data at: ' + job.get_target_alias())
                        notification_handler.resolve_notification(job)
                elif result['Exception'] == 'WorkerStatusException':
                    job.set_error('This Job was Canceled but the worker was in a different '
                                 'status, please contact your local administrator')
                    notification_handler.resolve_notification(job)
            job.set_status(JobStatus.CANCELED)
            job = self.look_for_work(worker)
            if job is not None:
                self.dequeue(job, worker)
            
    def resume_job(self, job):
        """
        resumes a paused job
        :param job: the job to resume
        :type job: Job
        @raises NoResponseFromWorkerException if the connection fails
        """
        job.set_status(JobStatus.ACTIVE)
        worker = Worker.get_worker_by_job_id(job.id)
        self.dequeue(job, worker)

    def look_for_work(self, worker):
        """
        Looks wether a job is available for the given worker
        :param worker: The worker to assign a job to
        :type worker: Worker
        :returns: a job
        """       
        storages = list(storage.alias for storage in worker.get_storages())
        jobs = Job.get_jobs(statuses=[JobStatus.QUEUED], storages=storages)
        if not jobs:
            return None
        else:
            return jobs[0]

    def dequeue(self, job: Job, worker: Worker):
        """
        Start working on a given job
        :param job: the job to start
        :param worker: the worker to assign to
        @raises NoResponseFromWorkerException if the connection fails
        """
        job.set_status('ACTIVE')
        priority = job.priority
        job.set_priority(None)
        result = self._master_communicator.assign_task(job, worker)
        if 'Exception' in result and result['Exception'] != 'None':
            if result['Exception'] == 'WorkerStatusException':
                worker.set_status(self._master_communicator.get_status(worker)['status'])
                if worker.get_status() == 'WAITING':
                    self.dequeue(job, worker)
                else: 
                    job.set_status('QUEUED')
                    job.set_priority(priority)
                    usable = Worker.get_idle_workers_for_storages(job.source_alias, job.target_alias)
                    if usable:
                         self.dequeue(job, usable[0])
            elif result['Exception'] == 'NamingConventionError':
                job.set_error('NamingConventionError: The source file has a Filename that does not fit the Convention')
                job.set_status('CANCELED')
                notification_handler.resolve_notification(job)

    def disable_worker(self, worker_id):
        """
        Disables a worker, updates database and sends message
        :param worker_id: id of worker to disable
        :type worker_id: integer
        @raises NoResponseFromWorkerException if the connection fails
        """
        worker = Worker.get_worker_by_id(worker_id)
        worker.set_status('DEACTIVATED')
        self._master_communicator.change_status_worker(worker, status='DEACTIVATED')

    def enable_worker(self, worker_id):
        """
        Enables a worker
        :param worker: Worker to enable
        :type worker: Worker
        @raises NoResponseFromWorkerException if the connection fails
        """
        worker = Worker.get_worker_by_id(worker_id)
        worker.set_status('WAITING')
        self._master_communicator.change_status_worker(worker, status='ACTIVE')
        job = self.look_for_work(worker)
        if job is not None:
            self.dequeue(job, worker)

    def worker_changed_status(self, status):
        """
        Gets called by the worker endpoint to signal a change in the status of a worker
        """
        worker = Worker.get_worker_by_name(status['worker_name'])
        worker.set_status(status['status'])
        if status['status'] == 'WAITING':
            worker.set_active_job(None)
            job = self.look_for_work(worker)
            if job is not None:
                self.dequeue(job, worker)

    def job_changed_status(self, status, ):
        # TODO getting job objects twice, because they expire after setting the status
        # how to do this better? maybe: set expire_on_commit=False
        job = Job.get_job_by_id(status['id'])
        if status['status'] in ['INITIALIZED', 'DELETED', 'COPYING', 'COPIED', 'CHECKED']:
            job.set_status(JobStatus.ACTIVE)
            job = Job.get_job_by_id(status['id'])
            Worker.get_worker_by_name(status['worker_name']).set_active_job(job)
        elif status['status'] in ['PAUSED', 'EXCEPTION', 'ERROR']:
            job.set_status(JobStatus.PAUSED)
            job = Job.get_job_by_id(status['id'])
            Worker.get_worker_by_name(status['worker_name']).set_active_job(job)
        elif status['status'] in ['TERMINATED']:
            job.set_status(JobStatus.CANCELED)
            job = Job.get_job_by_id(status['id'])
            Worker.get_worker_by_name(status['worker_name']).set_active_job(None)
        else:
            job.set_status(JobStatus.DONE)
            w = Workspaces.get_by_path(job.source_path)
            if not w: raise AttributeError('No Workspace entry was found. Location couldn\'t be updated.')
            w.set_full_path(job.target_path)
            w.set_storage(job.target_alias)

            job = Job.get_job_by_id(status['id'])
            Worker.get_worker_by_name(status['worker_name']).set_active_job(None)
        if 'start_time' in status and status['start_time'] is not None:
            job.set_start_time(dateutil.parser.parse(status['start_time']))
        if 'completion_time' in status and status['completion_time'] is not None:
            job.set_end_time( dateutil.parser.parse(status['completion_time']))
        if 'exceptions' in status and status['exceptions'] is not None:
            for e in status['exceptions']:
                job.set_error(e)
        if 'errors' in status and status['errors'] is not None:
            for err in status['errors']:
               job.set_error(err)
        notification_handler.resolve_notification(job)

    def add_job_stats(self, job_id, stats):
        job = Job.get_job_by_id(job_id)
        job.set_n_of_files(stats.get('n_of_files'))
        job.set_n_of_dirs(stats.get('n_of_dirs'))
        job.set_workpool_size(stats.get('total_size'))
        job.set_compression_rate(stats.get('compression_rate'))
        return

    def register_worker(self, worker_data):
        if not all (key in worker_data.keys() for key in('worker_name','address','status','mountpoints')):
            return { 'Exception' : 'Invalid or missing Data' }
        duplicate = Worker.get_worker_by_name(worker_data['worker_name']) 
        if duplicate is not None and worker_data['address'] != duplicate.get_address():
            return {
                    'Exception' : 'Worker id already taken'
                    }
        elif duplicate is not None and worker_data['address'] == duplicate.get_address():
            return
        worker = Worker(worker_data['worker_name'], worker_data['status'], None, worker_data['address'], worker_data['mountpoints'])
        if worker.get_status() == WorkerStatus.WAITING:
            job = self.look_for_work(worker)  
            if job is not None:
                self.dequeue(job, worker)
        
