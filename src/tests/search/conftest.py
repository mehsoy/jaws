import pytest
import subprocess
import grp
import pwd
import os


@pytest.fixture(scope='session')
def groupA(request):
    '''Creates a new group'''
    groupA = 'dmdtestgroup'
    while group_exists(groupA):
        groupA = groupA + 'fill'
    os.system(' '.join(['groupadd', groupA]))

    def fin():
        os.system(' '.join(['groupdel', groupA]))
    request.addfinalizer(fin)

    return groupA

def group_exists(groupA):
    try:
        grp.getgrnam(groupA)
        return True
    except KeyError:
        return False

@pytest.fixture(scope='session')
def userA(request, groupA):
    '''Creates a new user, who is a member of `groupA`'''
    userA = 'dmdtestuser'
    while user_exists(userA):
        userA = userA + 'a'
    os.system(' '.join(['useradd', userA]))
    os.system('usermod -a -G '+ groupA + ' ' +  userA)
    #check that the user is member of `groupA`
    assert groupA in subprocess.check_output('groups ' + userA, shell=True).decode('utf-8')

    def fin():
        os.system(' '.join(['userdel', '-r', userA]))
    request.addfinalizer(fin)

    return userA

def user_exists(userA):
    try:
        pwd.getpwnam(userA)
        return True
    except KeyError:
        return False

