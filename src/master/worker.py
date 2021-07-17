#!/usr/bin/python
#s-*- coding: utf-8 -*-

import sqlalchemy

from application.system.storage import Storage
from .worker_status import WorkerStatus

from application.system.job import Job
from database import meta

from sqlalchemy import create_engine, and_, Column, String, Integer, Enum, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import UniqueConstraint

#association Table for workers and storages
workers_has_storages = Table('workers_has_storages',
                            meta.Base.metadata,
                            Column('worker_id', Integer, ForeignKey('workers.id')),
                            Column('storage_alias', ForeignKey('storages.alias')),
                            UniqueConstraint('worker_id', 'storage_alias', name='1:n_worker_storage')
                            )


class Worker(meta.Base):
    """
    This class represents a worker which is managed by the Master. It connects to the dmd_data.sqlite3 Database.
    
    """
    __tablename__ = 'workers'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, unique=True)
    status = Column('status', Enum(WorkerStatus))  
    current_job_id = Column('current_job_id', ForeignKey(Job.id))
    address = Column('address', String)
    storages = relationship('Storage',
                secondary=workers_has_storages,
                backref='workers')

    def __init__(self, name, status, current_job, address, mountpoints):
        """
        Constructor for the Worker class, saves class attributes and commits to the database
        :param name: name of the worker
        :param status: status of the Worker
        :param current_job_id: id of the active job
        :param address: the base url
        :param storages_aliases: List of mounted storages
        """
        self.name = name
        self.status = status
        self.address = address
        if mountpoints is not None:
            mountpoints = list(set(mountpoints))
            for mountpoint in mountpoints:
                storage = Storage.get_storage_by_mountpoint(mountpoint)
                if storage is not None:
                    meta.get_session(storage).close()
                    self.storages.append(storage) 
                else:
                    pass
        if current_job is not None:
            self.current_job_id = current_job.id
        else:
            self.current_job_id = None
        session = meta.get_session(self)
        session.add(self)
        session.commit()

    def get_storages(self, ):
        """
        Basic getter for the storage list
        :returns self.storages()
        """
        session = meta.get_session(self)
        return self.storages

    def get_id(self):
        """
        Getter for ID
        :return: ID
        """
        return self.id

    def get_name(self):
        """
        Getter for name
        :return: Name
        """
        return self.name

    def get_status(self, ):
        """
        Basic getter for the status
        :returns self.status()
        """
        return self.status

    def get_address(self, ):
        """
        Basic getter for the adress

        :returns: the basis-url of the worker (usually its host)
        """
        return self.address

    def set_active_job(self, job):
        """
        Sets the active job for this worker and updates its status to active
        :param job the job to use
        :type job: Job
        """
        session = meta.get_session(self)
        session.add(self)
        self.current_job_id = job.id if job else None
        session.commit()

    def get_current_job(self):
        """
        Returns current job
        :return: Job
        """
        if self.current_job_id is not None:
            return Job.get_job_by_id(self.current_job_id)
        return None

    def set_status(self, status):
        """
        Sets the status
        :param status: status to set
        :type status: WorkerStatus
        """
        session = meta.get_session(self)
        self.status = status
        session.commit()
    
    def delete(self,):
        """
        Permanently deletes the worker. Can not be recovered
        """
        session = meta.get_session(self)
        session.delete(self)
        session.commit()

    @classmethod
    def get_all_workers(cls, ):
        """
        Returns a list of all the workers currently in the database
        :returns list of Worker
        """
        session = meta.Session()
        return session.query(cls).all()

    @classmethod
    def get_worker_by_id(cls, id):
        """
        Returns a worker with the given id or None
        :param id: id to look for
        :type id: int
        :returns Worker or None
        """
        session = meta.Session()
        return session.query(cls).filter(cls.id == id).one_or_none()

    @classmethod
    def get_worker_by_storages(cls, source, target):
        """
        Returns the first worker which can acces both storages
        :param source: alias of the source
        :param target: alias of the target
        :type source: String
        :type target: String
        returns: Worker
        """
        session = meta.Session()
        return session.query(cls).filter(and_(cls.storages.any(Storage.alias==source)),
                                            (cls.storages.any(Storage.alias==target)),
                                        ).all()

    @classmethod
    def get_idle_workers_for_storages(cls, source, target):
        """
        Returns the first worker which can acces both storages
        :param source: alias of the source
        :param target: alias of the target
        :type source: String
        :type target: String
        returns: Worker
        """
        session = meta.Session()
        return session.query(cls).filter(and_(cls.storages.any(Storage.alias==source)),
                                            (cls.storages.any(Storage.alias==target)),
                                         (cls.status==WorkerStatus.WAITING.name)
                                        ).all()

    @classmethod
    def get_worker_by_name(cls, name):
        """
        Returns an Worker with the given name.
        returns: Worker
        """
        session = meta.Session()
        return session.query(Worker).filter(cls.name==name).first()

    @classmethod
    def get_worker_by_job_id(cls, id):
        session = meta.Session()
        return session.query(Worker).filter(cls.current_job_id == id).one_or_none()

