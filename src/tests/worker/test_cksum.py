#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pytest


from worker.cksum import Cksum
from worker.task import Task
from worker.task_status import TaskStatus

from exceptions.copy_not_successfull_exception import CopyNotSuccessfullException

# TODO
# @pytest.fixture
# def cksum():
#     return Cksum()
#
#
# @pytest.fixture
# def task():
#     # build test environment
#     TestHelper.build_test_environment(os.getcwd() + "/src/tests/worker/test_material/")
#     task = Task(2, "mock_source_alias3", "mock_path3", "mock_target_alias3")
#     task.set_copytool(Rsync(0, OutStub(), '-asv --inplace', cksum))
#     yield task
#     # now tear down test environment
#     TestHelper.destroy_test_evironment(os.getcwd() + "/src/tests/worker/test_material/")
#
#
# @pytest.fixture
# def task_file(task):
#     workpath = os.getcwd()
#     task.set_absolute_source_path(workpath
#                                   + "/src/tests/worker/test_material/johann-directory-1/cksum_testfile1.txt")
#     task.set_absolute_target_path(workpath
#                                   + "/src/tests/worker/test_material/johann-test_dir-1/testfile1.txt")
#     return task
#
#
# @pytest.fixture
# def task_nofile(task):
#     workpath = os.getcwd()
#     task.set_absolute_source_path(workpath
#                                   + "/src/tests/worker/test_material/johann-directory-1/cksum_testfile1.txt")
#     task.set_absolute_target_path(workpath
#                                   + "/src/tests/worker/test_material/johann-directory-1/nonexistant_file.txt")
#     return task
#
#
# @pytest.fixture
# def task_dir(task):
#     workpath = os.getcwd()
#     task.set_absolute_source_path(workpath + "/src/tests/worker/test_material/johann-directory-1")
#     task.set_absolute_target_path(workpath + "/src/tests/worker/test_material/johann-test_dir-1")
#     return task
#
#
# @pytest.fixture
# def task_samedir(task):
#     workpath = os.getcwd()
#     task.set_absolute_source_path(workpath + "/src/tests/worker/test_material/johann-directory-1")
#     task.set_absolute_target_path(workpath + "/src/tests/worker/test_material/johann-directory-1")
#     return task
#
#
# @pytest.fixture
# def task_different(task):
#     workpath = os.getcwd()
#     task.set_absolute_source_path(workpath
#                                   + "/src/tests/worker/test_material/johann-directory-1/cksum_testfile1.txt")
#     task.set_absolute_target_path(workpath
#                                   + "/src/tests/worker/test_material/johann-directory-1/cksum_testfile2.txt")
#     return task
#
#
# def test_copyfile(cksum, task_file):
#     task = task_file
#     task = cksum.consistency_check(task)
#     assert task.get_status() == TaskStatus.CHECKED
#
#
# def test_nofile(cksum, task_nofile):
#     task = task_nofile
#     task = cksum.consistency_check(task)
#     assert task.get_status() == TaskStatus.EXCEPTION
#     # (CopyNotSuccessfullException)
#
#
# def test_copydir(cksum, task_dir):
#     task = task_dir
#     task = cksum.consistency_check(task)
#     assert task.get_status() == TaskStatus.CHECKED
#
#
# def test_samedir(cksum, task_samedir):
#     task = task_samedir
#     task = cksum.consistency_check(task)
#     assert task.get_status() == TaskStatus.CHECKED
#
#
# def test_different(cksum, task_different):
#     task = task_different
#     task = cksum.consistency_check(task)
#     assert task.get_status() == TaskStatus.EXCEPTION
#     assert isinstance(task.get_exceptions()[0], CopyNotSuccessfullException)
#     # (CopyNotSuccessfullException)
