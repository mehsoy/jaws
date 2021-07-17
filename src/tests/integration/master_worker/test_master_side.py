#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import pytest
import time

import tests.worker.test_helper as TestHelper

from exceptions.user_not_found_exception import UserNotFoundException
from database import meta
from master.master import Master
from application.system.job import Job
from application.system.user import User
'''
How to Test:

auf .127 (dmd-5) 
    Sicherstellen dmd_data.sqlite3 ist in implementation/database
    Bei Bedarf (wenn Registrerung getestet werden soll: 'sqlite3 database/dmd_data.sqlite3 < database/clear_database.sql'
    Master starten mit 'dmdmaster src/master/config.ini'

auf .32 (dmd-2)
    Worker starten mit 'dmdworker src/worker/config.ini'

Wenn es keine Probleme bei der registrierung gab ist es kein Problem zwecks pull nur eine Seite neu zu starten

'''
@pytest.fixture
def env():
    #We must have some files be created automatically on centos 32 for it to be moved.
    TestHelper.build_test_environment("/mount/master_data/tests/")
    yield
    TestHelper.remove_file("/export/archive1/1-johann-directory.tar")
    TestHelper.destroy_test_evironment("/mount/master_data/tests/")

def test_success_job(env):
    try:
        johann = User.get_user_by_username('johann')
    except UserNotFoundException:
        johann = User('johann', 'jtoken')
    job = Job(source_alias = 'dmd_home', target_alias = 'archive1', 
              source_relative_path = 'export/master_data/tests/johann-directory-1', 
              notification = [False, False, False], user = johann)
    job_id = job.id
    master = Master.get_master()
    worker = master.get_workers()[0]
    assert worker.name == 'worker1'
    assert worker.status.name == 'WAITING'
    master.add_to_queue(job)
    time.sleep(5)
    while (worker.status.name == 'ACTIVE'):
        #wait for worker to finish
        time.sleep(5)
    assert worker.status.name == 'WAITING'
    assert Job.get_job_by_id(job_id).status.name == 'DONE'
    #make sure the file was actually copied
    assert os.path.exists("/export/archive1/1-johann-directory.tar")
    
def test_cancel_job():
    try:
        johann = User.get_user_by_username('johann')
    except UserNotFoundException:
        johann = User('johann', 'jtoken')
    job = Job('dmd_home', 'dmd1', 'home/centos/testdata/johann-directory-1', [False, False, False], johann)
    job_id = job.id
    master = Master.get_master()
    master.add_to_queue(job)
    master.cancel_job(job)

    worker = master.get_workers()[0]

    assert worker.name == 'worker1'
    assert worker.status.name == 'WAITING'
    assert Job.get_job_by_id(job_id).status.name == 'CANCELED'
