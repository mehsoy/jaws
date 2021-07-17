#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import sys
import pytest

from search.search_class import Search
from search.search_storage import SearchStorage
from search.config_handler import ConfigHandler


path = os.getcwd()
config_handler = ConfigHandler(path + '/src/tests/search/test_config.ini')
storages = config_handler.get_storages()
test_directories_paths = []
test_directories_paths.append('/mount/dmd5/centostest1-directory-1')
test_directories_paths.append('/mount/dmd5/centostest1-directory-2')
test_directories_paths.append('/mount/dmd5/directory-1-mustermanntest1')
test_directories_paths.append('/mount/dmd5/mustermanntest1-directory-2')


@pytest.fixture()
def setup_teardown():
    for path in test_directories_paths:
        os.makedirs(path, exist_ok = True)
    yield
    for path in test_directories_paths:
        os.rmdir(path)       

def test_basic_getters():
    storage = storages['dmd_home']
    assert storage.get_naming_convention() == "<username>-<alias>-<count>"
    assert storage.has_home_directory() == True
    assert storage.is_archive() == False
    assert storage.does_accept_jobs() == True
    storage.set_accept_jobs(False)
    assert storage.does_accept_jobs() == False
    storage.set_accept_jobs(True)
    assert storage.does_accept_jobs() == True
    pass
    
def test_get_user_credentials():
    assert 'thisisacredentialsstring123456randomnumbers' == storages['dmd_home'].get_user_credentials('centos')
    
def test_search_for_directories(setup_teardown):
    usernames = ['centostest1']
    userdirs = storages['dmd5'].search_for_directories(usernames)
    expected_directories = ['/mount/dmd5/centostest1-directory-1', '/mount/dmd5/centostest1-directory-2']
    assert len(expected_directories) == len(userdirs)
    assert sorted(userdirs) == expected_directories
    
def test_search_for_directories_with_multiple_usernames(setup_teardown): 
    usernames = ['centostest1', 'mustermanntest1']
    userdirs = storages['dmd5'].search_for_directories(usernames)
    expected_directories = test_directories_paths
    assert len(expected_directories) == len(userdirs)
    assert sorted(userdirs) == expected_directories    
