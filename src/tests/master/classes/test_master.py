import pytest

from exceptions.user_not_found_exception import UserNotFoundException
from master.master import Master
from master.worker import Worker

from application.system.job import Job
from application.system.user import User
"""
This test assumes an empty database
"""
try:
    user = User.get_user_by_username("xyz")
except UserNotFoundException:
    user = User("xyz", "token")
jobA = Job('storageA', 'storageB', '~/.data/', [True, True, True], user)
jobB = Job('storageB', 'storageC', '~/.data/', [True, True, True], user)
jobC = Job('storageC', 'storageD', '~/.data/', [True, True, True], user)   
   
workerA = Worker('A', 'WAITING', None, 'host:1234', ['storageA', 'storageB'])
workerB = Worker('B', 'WAITING', None, 'host:1234', ['storageA', 'storageB'])

@pytest.mark.order1
def test_constructor():
    master = Master.get_master()
    assert(type(master) is Master) 
    
    master2 = Master.get_master()
    assert(master == master2)

