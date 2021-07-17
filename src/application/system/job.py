#!/usr/bin/python
#-*- coding: utf-8 -*-

import sqlalchemy
import datetime

from sqlalchemy import create_engine, Column, String, Integer, Boolean, Enum, DateTime, Table, ForeignKey, or_

from database import meta

from .user import User
from .job_status import JobStatus
from exceptions.job_not_found_exception import JobNotFoundException

from typing import List


class Job(meta.Base):
    """
    Represents a job. Part of ORM model in the database
    """
    __tablename__ = 'jobs'
    id = Column('id', Integer, primary_key=True)
    user = Column('user_name', String, ForeignKey(User.name))
    source_alias = Column('source_alias', String, nullable=False)
    target_alias = Column('target_alias', String, nullable=False)
    source_path = Column('source_path', String)
    priority = Column('priority', Integer, unique=True)
    error = Column('error', String, default=None)
    notification_abort = Column('notification_abort', Boolean, default=False)
    notification_begin = Column('notification_begin', Boolean, default=False)
    notification_end = Column('notification_end', Boolean, default=False)
    started_at = Column('started_at', DateTime)
    enqueued_at = Column('enqueued_at', DateTime)
    ended_at = Column('ended_at', DateTime)
    status = Column('status', Enum(JobStatus))
    n_of_files = Column('n_of_files', Integer, default=None)
    n_of_dirs = Column('n_of_dirs', Integer, default=None)
    workpool_size = Column('workpool_size', Integer, default=None)
    compression_rate = Column('compression_rate', Integer, default=None)
    target_path = Column(String)
    copy_options = Column(String)

    def __init__(self, source_alias: str, target_alias: str, source_path: str, notification, user=None, target_path: str=None, copy_options=None):
        
        self.source_alias = source_alias
        self.target_alias = target_alias
        self.source_path = source_path
        self.target_path = target_path
        #self.status = JobStatus.QUEUED
        self.user = user.get_username()
        self.copy_options = copy_options

        if notification is not None:
            self.notification_abort = notification[0]
            self.notification_begin = notification[1]
            self.notification_end = notification[2]
        
        session = meta.get_session(self)
        session.add(self)
        session.commit()

    @classmethod
    def get_job_by_id(cls, job_id):
        """
        Returns a Job with the given id or None
        :param id: id to look for
        :type id: int
        :returns Job or None
        """
        session = meta.Session()
        job = session.query(cls).filter(cls.id==job_id).one_or_none()
        if job is None:
            raise JobNotFoundException("Job with ID " + str(job_id) + " doesn't exist")
        return job

    @classmethod
    def get_job_by_priority(cls, priority):
        session = meta.Session()
        return session.query(cls).filter(cls.status=='QUEUED', cls.priority==priority).one_or_none()
    
    @classmethod
    def get_job_lowest_priority(cls):
        session = meta.Session()
        return session.query(cls).filter(cls.status=='QUEUED').order_by(cls.priority).first()
    
    @classmethod
    def get_job_highest_priority(cls):
        session = meta.Session()
        return session.query(cls).filter(cls.status=='QUEUED').order_by(cls.priority.desc()).first()
 
    @classmethod
    def get_jobs(cls, users=None, statuses: List[JobStatus] = None, days=None, storages=None):
        """
        Returns Jobs, filter by:
        :param days: how many days in the past
        :param users: List of users they may belong to
        :param statuses: their status
        :param storages: List of storage aliases
        :type storages: List<String>
        :type days: int
        :type users: List<User>
        """
        session = meta.Session()
        jobs = session.query(cls)
        intersection = []

        if days is not None:
            days = int(days)
            intersection = jobs.filter(cls.ended_at >= datetime.date.today() - datetime.timedelta(days=days)).all()
        if users is not None:
            jobs = jobs.filter(cls.user.in_(users))
            intersection = jobs if not intersection else list(set(intersection) & set(jobs.all()))
        if statuses is not None:
            jobs = jobs.filter(cls.status.in_(statuses))
            intersection = jobs if not intersection else list(set(intersection) & set(jobs.all()))
        if storages is not None:
            jobs = jobs.filter(or_(cls.source_alias.in_(storages), cls.target_alias.in_(storages)))
            intersection = jobs if not intersection else list(set(intersection) & set(jobs.all()))

        return intersection

    def get_job_id(self):
        """
        Returns the id
        :returns: id
        """
        return self.id

    def get_source_alias(self):
        """
        Returns the source alias
        :returns: source_alias
        """
        return self.source_alias

    def get_target_alias(self):
        """
        Returns the target alias
        :returns: target_alias
        """
        return self.target_alias

    def get_source_path(self):
        return self.source_path

    def get_user(self):
        """
        Returns the user created this job
        :return: user
        """
        return User.get_user_by_username(self.user)

    def get_start_time(self):
        """
        Returns the time at which the job was started
        :returns: started_at
        """
        return self.started_at

    def set_start_time(self, start_time):
        """
        Sets the time at which the job was started
        :param start_time: the time to set
        :type start_time: datetime
        """
        session = meta.get_session(self)
        self.started_at = start_time
        session.commit()

    def get_end_time(self):
        """
        Returns the time at which the job was finished
        :returns: ended_at
        """
        return self.ended_at

    def set_end_time(self, end_time):
        """
        Sets the time at which the job was finshed
        :param end_time: the time
        :type end_time: datetime
        """
        session = meta.get_session(self)
        self.ended_at = end_time
        session.commit()

    def get_enqueue_time(self):
        """
        Returns the time at which the job was accepted by the master.
        :returns: enqeued_at
        """
        return self.enqueued_at

    def set_enqueue_time(self, enqueued_at):
        """
        Sets the time at which the job was accepted by the master
        :param enqueued_at: the time
        :type enqueued_at: datetime
        """
        session = meta.get_session(self)
        self.enqueued_at = enqueued_at
        session.commit()

    def get_status(self):
        """
        Returns the current status
        :returns: status
        """
        return self.status

    def set_status(self, status):
        session = meta.get_session(self)
        self.status = status
        session.commit()

    def get_priority(self):
        """
        returns the current priority
        :returns: priority
        """
        return self.priority

    def set_priority(self, priority):
        """"
        Sets the priority
        :param priority: the new priority
        :type priority: int
        """
        session = meta.get_session(self)
        self.priority = priority
        session.commit()

    def get_error(self):
        """
        Returns the error message associated with this job
        :returns: error
        """
        return self.error

    def set_error(self, error):
        """
        Adds an error
        :param error: the error
        :type error: String (???)
        """
        session = meta.get_session(self)
        self.error = error
        session.commit()

    def get_n_of_files(self):
        return self.n_of_files

    def set_n_of_files(self, n):
        session = meta.get_session(self)
        self.n_of_files = n
        session.commit()

    def get_n_of_dirs(self):
        return self.n_of_dirs

    def set_n_of_dirs(self, n):
        session = meta.get_session(self)
        self.n_of_dirs = n
        session.commit()

    def get_workpool_size(self):
        return self.workpool_size

    def set_workpool_size(self, size):
        session = meta.get_session(self)
        self.workpool_size = size
        session.commit()

    def get_compression_rate(self):
        return self.compression_rate

    def set_compression_rate(self, rate):
        session = meta.get_session(self)
        self.compression_rate = rate
        session.commit()

    def has_start_notification(self):
        """
        Returns whether the job sends a Notificaiton on start
        """
        return self.notification_begin

    def has_end_notification(self):
        """
        Returns whether the job sends a Notificaiton on end
        """
        return self.notification_end

    def has_error_notification(self):
        """
        Returns whether the job sends a Notification when an error occures/it ist aborted
        """
        return self.notification_abort 

    def remove(self):
        """
        Deletes the job. WARNING: THIS IS NOT REVERSIBLE. 
        Deleted Jobs can not be recovered.
        """
        session = meta.get_session(self)
        session.delete(self)
        session.commit()
