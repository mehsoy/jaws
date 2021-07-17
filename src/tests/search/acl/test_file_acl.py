import grp
import os 
import pwd
import pytest

from posix1e import ACL_READ, ACL_WRITE, ACL_EXECUTE
from search.posix import Posix as FileACL


'''
Tests for this module must be run as root, since new files, groups and users 
are created and deleted in the process of setting/tearing the test environment
up/down, which requites root permissions.
'''

test_parameters = [
	('=---', '---'),
	('+r', 'r--'),
	('+w', 'rw-'),
	('+x', 'rwx'),
	('-x', 'rw-'),
	('-r', '-w-'),
	('-w', '---'),
	('+rw', 'rw-'),
	('+wx', 'rwx'),
	('-rx', '-w-'),
	('+rwx', 'rwx'),
	('+', 'rwx'),
	('-wx', 'r--'),
	('=rwx', 'rwx'),
	('=r', 'r--'),
	('=wx', '-wx'),
	('=', '---'),
]

@pytest.fixture
def fresh_file(request):
    filename = 'fresh_file1234.txt'
    #Gets parent directory of this file and append `filename`
    filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    #Creates a file
    open(filepath, 'w').close()

    def fin():
        os.remove(filepath)
    request.addfinalizer(fin)

    return filepath

@pytest.fixture(scope='module')
def module_file(request):
    filename = 'module_file1234.txt'
    #Gets parent directory of this file and append `filename`
    filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    #Creates a file
    open(filepath, 'w').close()

    def fin():
        os.remove(filepath)
    request.addfinalizer(fin)

    return filepath

@pytest.mark.parametrize('string, expected_tuple', [
    ('rwx', ({ACL_READ, ACL_WRITE, ACL_EXECUTE}, set())),
    ('+x', ({ACL_EXECUTE}, {ACL_READ, ACL_WRITE})),
    ('-x', ({ACL_EXECUTE}, {ACL_READ, ACL_WRITE})),
    ('=rw', ({ACL_READ, ACL_WRITE}, {ACL_EXECUTE})),
])
def test_extract_perm_occurrence(string, expected_tuple):
    assert FileACL.extract_perm_occurrence(string) == expected_tuple
    
####
## user-specific tests
####

def test_read_user(module_file, userA):
    os.system('setfacl -m u:' + userA + ':rwx ' + module_file)
    acl = FileACL(file=module_file)
    assert acl.get_perm_of('user', userA) == 'rwx'

    os.system('setfacl -m u:' + userA + ':--- ' + module_file)
    acl = FileACL(file=module_file)
    assert acl.get_perm_of('user', userA) == '---'

def test_apply_to_file(module_file, userA):
    os.system('setfacl -m u:' + userA + ':--- ' + module_file)
    acl = FileACL(file=module_file)
    acl.put_permission('user', userA, '+rwx')
    assert acl.get_perm_of('user', userA) == 'rwx'

    # Creating a new FileACL object makes sure that permissions
    # are actually written to Inode and are not just stored inside
    # the FileACL object
    acl = FileACL(file=module_file)
    assert acl.get_perm_of('user', userA) == 'rwx'

@pytest.mark.parametrize('instruction, expected_permset', test_parameters)
def test_write_user(module_file, userA, instruction, expected_permset):
    acl = FileACL(file=module_file)
    acl.put_permission('user', userA, instruction)
    assert acl.get_perm_of('user', userA) == expected_permset

####
## group-specific tests
####

def test_read_group(module_file, groupA):
    os.system('setfacl -m g:' + groupA + ':rwx ' + module_file)
    acl = FileACL(file=module_file)
    assert acl.get_perm_of('group', groupA) == 'rwx'

    os.system('setfacl -m g:' + groupA + ':--- ' + module_file)
    acl = FileACL(file=module_file)
    assert acl.get_perm_of('group', groupA) == '---'

@pytest.mark.parametrize('instruction, expected_permset', test_parameters)
def test_write_group(module_file, groupA, instruction, expected_permset):
    acl = FileACL(file=module_file)
    acl.put_permission('group', groupA , instruction)
    assert acl.get_perm_of('group', groupA) == expected_permset

####
## test user-group dynamic
####

def test_group_membership(fresh_file, userA, groupA):
    '''Tests that a user has access to a file (only) through group membership.
    
    This test assumes the user has no individual acl entry.'''
    acl = FileACL(file=fresh_file)
    acl.put_permission('group', groupA , '=r')
    assert acl.get_perm_of('group', groupA) == 'r--'
    acl.put_permission('other', None , '=')
    
    assert acl.user_has_perm(userA, 'r')



