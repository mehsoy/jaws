import pytest

from master import *
from master.worker import Worker
from master.worker_status import WorkerStatus

from application.system.job import Job
from application.system.user import User

from exceptions.user_not_found_exception import UserNotFoundException

try:
    user = User.get_user_by_username("xyz")
except UserNotFoundException:
    user = User("xyz", "token")

job = Job.get_jobs([user.name])
if job == []:
    job = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
  
@pytest.mark.order1
def test_constructor():
    if Worker.get_worker_by_name('testworker') is None:
        test_worker = Worker('testworker','WAITING', None, 'asdf@localhost', ['storageA', 'storageB'])
    else:
        test_worker = Worker.get_worker_by_name('testworker')
    assert type(test_worker) is Worker

@pytest.mark.order2
def test_get_by_name():
    worker = Worker.get_worker_by_name('testworker')
    assert worker.name == 'testworker'

@pytest.mark.order3
def test_getter():
    test_worker = Worker.get_worker_by_name('testworker')

    assert (type(test_worker.get_status()) == WorkerStatus)
    names= list(storage.alias for storage in test_worker.get_storages())   
    assert names  ==  ['storageA', 'storageB']  
    assert test_worker.get_address() == 'asdf@localhost'
    test_worker2 = Worker.get_worker_by_storages('storageA','storageB')
    assert test_worker.id ==  test_worker2.id
    
    test_worker3 = Worker.get_worker_by_storages('storageB','storageA')
    assert test_worker3.id ==  test_worker2.id

 
