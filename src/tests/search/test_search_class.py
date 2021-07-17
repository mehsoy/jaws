#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import pytest

from search.search_class import Search
from search.search_storage import SearchStorage
from search.config_handler import ConfigHandler
from exceptions.storage_not_mounted_error import StorageNotMountedError
from exceptions.storage_not_mounted_exception import StorageNotMountedException
from exceptions.incorrect_config_file_error import IncorrectConfigFileError
from exceptions.storage_alias_not_found_exception import StorageAliasNotFoundException
from exceptions.source_path_not_valid_exception import SourcePathNotValidException
from exceptions.storage_type_compatibility_exception import StorageTypeCompatibilityException



path = os.getcwd()

config_handler = ConfigHandler(path + '/src/tests/search/test_config.ini')
storages = config_handler.get_storages()
search = Search(storages, config_handler)

wrong_config_handler = ConfigHandler(path + '/src/tests/search/wrong_mountpoint_config.ini')
wrong_storages = wrong_config_handler.get_storages()
wrong_search = Search(wrong_storages, wrong_config_handler)

test_directories_paths = []
test_directories_paths.append('/mount/dmd5/centostest2-newdir')
test_directories_paths.append('/mount/dmd5/centostest2-seconddir')
test_directories_paths.append('/mount/dmd5/thirddir-centostest2')
test_directories_paths.append('/mount/centos127/someuser2-memories-1')
test_directories_paths.append('/mount/centos127/someuser2-memories-2')
test_directories_paths.append('/mount/centos127/someuser2-experiments-1')
test_directories_paths.append('/mount/archive1/someuser2-first_directory')
test_directories_paths.append('/mount/archive1/someuser2-first_directory/subdir')
test_directories_paths.append('/mount/archive1/someuser2-second_directory')
test_directories_paths.append('/mount/dmd5/mustermanntest2-directory-2')


@pytest.fixture()
def setup_teardown():
    for path in test_directories_paths:
        os.makedirs(path, exist_ok = True)
    yield
    for path in test_directories_paths:
        try: 
          os.rmdir(path) 
        except OSError:
          pass

#test getting directories with different naming conventions for one user
def test_get_directory_list_no_target_one_user(setup_teardown):
    usernames = ['centostest2']
    userdirs = search.get_directory_list(usernames)
    expected_directories = {'dmd5': ['centostest2-newdir', 'centostest2-seconddir', 'thirddir-centostest2'], 'centos': [], 'dmd_home': [], 'archive1': []}
    for key in expected_directories.keys():
      assert sorted(expected_directories[key]) == sorted(userdirs[key])

#test getting directories from different mountpoints for one user   
def test_get_directory_list_no_target_one_user_2(setup_teardown):
    usernames = ['someuser2']
    userdirs = search.get_directory_list(usernames)
    expected_directories = {'dmd5': [], 'centos': ['someuser2-memories-1' , 'someuser2-memories-2', 'someuser2-experiments-1'], 'dmd_home': [], 'archive1': ['someuser2-first_directory', 'someuser2-second_directory']}
    for key in expected_directories.keys():
      assert sorted(expected_directories[key]) == sorted(userdirs[key])      

def test_get_directory_list_no_target_for_multiple_users(setup_teardown):   
    usernames = ['centostest2', 'mustermanntest2']
    userdirs = search.get_directory_list(usernames)
    expected_directories = {'dmd5': ['centostest2-newdir', 'centostest2-seconddir', 'mustermanntest2-directory-2', 'thirddir-centostest2'], 'centos': [], 'dmd_home': [], 'archive1': []}
    for key in expected_directories.keys():
      assert sorted(expected_directories[key]) == sorted(userdirs[key])  


def test_get_directory_list_with_target_for_multiple_users(setup_teardown):   
    usernames = ['centostest2', 'mustermanntest2']
    userdirs = search.get_directory_list(usernames, 'dmd5')
    expected_directories = {'dmd5': ['centostest2-newdir', 'centostest2-seconddir', 'mustermanntest2-directory-2', 'thirddir-centostest2']}
    for key in expected_directories.keys():
      assert sorted(expected_directories[key]) == sorted(userdirs[key])  
      
def test_get_directory_list_with_target_with_caller(setup_teardown, userA, groupA):
    usernames = ['centostest2']
    #make files in storage `dmd5` not publicly available through `other` entry in acl
    for path in ['/mount/dmd5/thirddir-centostest2','/mount/dmd5/centostest2-seconddir','/mount/dmd5/centostest2-newdir']: 
        search.put_permission('other', None, '=---', path)
    #give user access to newdir through individual acl user entry
    search.put_permission('user', userA, '+r', '/mount/dmd5/centostest2-newdir')
    #give user access to seconddir through group membership
    search.put_permission('group', groupA, '+r', '/mount/dmd5/centostest2-seconddir')
    expected_directories = search.get_directory_list(usernames, 'dmd5', userA)
    assert expected_directories == { 'dmd5' : ['centostest2-newdir', 'centostest2-seconddir'] }

    
def test_get_storage_by_alias():
    storage = search.get_storage_by_alias('dmd5')
    assert storage.alias == 'dmd5'
    assert storage.mountpoint == '/mount/dmd5'

def test_resolve_abs_address(setup_teardown):
    alias_and_rel_path = search.resolve_abs_address('/mount/centos127/someuser2-memories-1')
    assert alias_and_rel_path[0] == 'centos'
    assert alias_and_rel_path[1] == 'someuser2-memories-1'
    
def test_resolve_abs_address_with_no_rel_path():    
    alias_and_rel_path = search.resolve_abs_address('/mount/archive1')
    assert alias_and_rel_path[0] == 'archive1'
    assert alias_and_rel_path[1] == ''
    
def test_resolve_abs_address_with_false_path():    
    with pytest.raises(SourcePathNotValidException):
      alias_and_rel_path = search.resolve_abs_address('mount/banana') 
    
def test_set_storage_accept_jobs():
    initial_status = search.get_storage_by_alias('archive1').does_accept_jobs()
    assert search._config_handler._config_parser.getboolean('archive1', 'storage_accept_jobs') == initial_status
    new_status = not(initial_status)
    search.set_storage_accept_jobs('archive1', new_status)
    assert search._config_handler._config_parser.getboolean('archive1', 'storage_accept_jobs') == new_status
    assert search.get_storage_by_alias('archive1').does_accept_jobs() == new_status
    search.set_storage_accept_jobs('archive1', initial_status)
    

def test_verify_job_expected_ok(setup_teardown):
     assert search.verify_job('/mount/dmd5/centostest2-newdir', 'dmd5') == {'source_relative_path': 'centostest2-newdir', 'target_alias': 'dmd5', 'source_alias': 'dmd5'}
     
def test_verify_job_wrong_target_alias(setup_teardown):
     with pytest.raises(StorageAliasNotFoundException):
       search.verify_job('/mount/dmd5/centostest2-newdir', 'not_existing_alias')

def test_verify_job_wrong_source_absolute_path():
     with pytest.raises(SourcePathNotValidException):
       search.verify_job('/mount/dmd5/centos-seconddir/not_existing_storage', 'archive1') 
       
def test_verify_job_not_compatible_storages():
     with pytest.raises(StorageTypeCompatibilityException):
       search.verify_job('/mount/archive1/someuser2-first_directory', 'archive1')   
                    
    
def test_check_storage_type_compatibility():
    assert search.check_storage_type_compatibility(storages['dmd5'], storages['archive1']) == True

def test_check_storages_mount():
    assert search.check_storages_mount(storages) == True
    with pytest.raises(StorageNotMountedError):
      search.check_storages_mount(wrong_storages)
    
def test_check_storage_mount():
    mounted_storage = storages['archive1']
    not_mounted_storage = wrong_storages['dmd5']
    assert search.check_storage_mount(mounted_storage) == True
    with pytest.raises(StorageNotMountedError):
      search.check_storage_mount(not_mounted_storage)
    
def test_get_storage_by_alias():
    storage = search.get_storage_by_alias('dmd_home')
    with pytest.raises(StorageAliasNotFoundException):
      storage = search.get_storage_by_alias('banana')

def test_verify_target():
    assert search.verify_target('dmd5').mountpoint == '/mount/dmd5'
    with pytest.raises(StorageAliasNotFoundException):
      search.verify_target('banana2')
    
    
 
