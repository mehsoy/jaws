#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import pytest
import os.path
import subprocess


from worker.storage import Storage
from worker.task import Task
from worker.task_status import TaskStatus
from worker.cksum import Cksum
from worker.worker_class import Worker
from worker.msg_in import MsgIn
from worker.msg_out import Out

from exceptions.copy_fail_error import CopyFailError
from exceptions.source_path_not_valid_exception import SourcePathNotValidException
from exceptions.copy_process_failed_exception import CopyProcessFailedException
from exceptions.copy_sequence_exception import CopySequenceException

#TODO
#check if the tar version does not return negative values at error!
#following problem: at execution with tar 1.24:
#
################################################################################################################
# command = ['tar', '-c', '-f', '/home/centos/dmd/implementation/tests/worker/test_material/moved/             #
# non_existant_dir/test.tar', '-z', '-H', 'posix', '-p', '--no-ignore-command-error', '-C', '/home/centos/dmd/ #
# implementation/src/tests/worker/test_material/', 'test_dir']                                                 #
#                                                                                                              #
# tar return value = -13                                                                                       #
#                                                                                                              #
# negative values are currently interpreted as exit                                                            #
#                                                                                                              #
################################################################################################################
# def task_c():
#     tar = Tar(0, Out("/mock/address", "master_secret", 60000, 1000))
#     workpath = os.getcwd()
#     #build test environment
#     TestHelper.build_test_environment(workpath + "/src/tests/worker/test_material/")
#     task = Task(1, "source_alias", "testfile1", "target_alias")
#     task.set_worker_name("w2")
#     task.set_copytool(tar)
#     #standard value
#     task.set_special_tool_options("-c")
#     task.set_source_storage(Storage("source_alias",workpath + "/src/tests/worker/test_material/", tar))
#     task.set_target_storage(Storage("target_alias",workpath+"/src/tests/worker/test_material/moved/", tar))
#     task.set_status(TaskStatus.INITIALIZED)
#     return task
#     #now tear down test environment
#     TestHelper.destroy_test_evironment(workpath + "/src/tests/worker/test_material/")
#
# def task_noex_target():
#     task = task_c()
#     workpath = os.getcwd()
#     task.set_absolute_source_path(workpath + "/src/tests/worker/test_material/test_dir")
#     task.set_relative_source_path("test_dir")
#     task.set_absolute_target_path(workpath
#                                   + "/tests/worker/test_material/moved/non_existant_dir/test.tar")
#     task.set_relative_target_path("test.tar")
#     return task
#
# def test_not_existing_targetdir():
#     task = task_noex_target()
#     #(CopyFailError):
#     task = task.get_copytool().copy(task)
#     assert task.get_status() == TaskStatus.ERROR
#     assert isinstance(task.get_errors()[0], CopyFailError)
#     assert os.path.exists(task.get_absolute_target_path()) == False
#     TestHelper.destroy_test_evironment(os.getcwd() + "/src/tests/worker/test_material/")
#
#
# test_not_existing_targetdir()
