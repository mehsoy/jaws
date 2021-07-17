#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess

from worker.task import Task
from worker.task_status import TaskStatus
from worker.copytool import Copytool
from exceptions.source_path_not_valid_exception import SourcePathNotValidException


class TestHelper:
    @staticmethod
    def destroy_test_evironment(test_dir: str):
        # to unblock the readonly_dir we use Copytool.unblock_source_file()
        task = Task(1, "xxx", "yyy", "zzz")
        task.absolute_source_path = test_dir
        TestHelper.unblock_source_file(task)
        # now we can just remove all
        TestHelper.remove_dir(test_dir)
        # and recreate it
        TestHelper._mkdir(test_dir)

    @staticmethod
    def build_test_environment(test_dir: str):
        # just to avoid conflicts in mkdir and make sure testenvironment is created
        TestHelper.destroy_test_evironment(test_dir)
        # build directories
        TestHelper._mkdir(test_dir + "centos-directory-1")
        TestHelper._mkdir(test_dir + "centos-directory-1/subdir")
        TestHelper._mkdir(test_dir + "centos-test_dir-1")
        TestHelper._mkdir(test_dir + "centos-test_dir-1/subdir")
        TestHelper._mkdir(test_dir + "moved")
        TestHelper._mkdir(test_dir + "extract")
        # to construct the readonly_dir we use Copytool.block_source_file()
        TestHelper._mkdir(test_dir + "centos-readonly_dir-1")
        task = Task(1, "xxx", "yyy", "zzz")
        task.absolute_source_path = test_dir + "centos-readonly_dir-1"
        TestHelper.block_source_file(task)

        TestHelper._mkfile(test_dir + "centos-testfile-1.txt", "test successful\nother value")
        TestHelper._mkfile(test_dir + "centos-test_dir-1/testfile1.txt", "test successful\nother value")
        TestHelper._mkfile(test_dir + "centos-test_dir-1/testfile2.txt", "test successful")
        TestHelper._mkfile(test_dir + "centos-test_dir-1/subdir/testfile1.txt",
                           "test successful\nother value")
        TestHelper._mkfile(test_dir + "centos-test_dir-1/subdir/testfile2.txt", "test successful")

        TestHelper._mkfile(test_dir + "centos-directory-1/cksum_testfile1.txt", "test successful\nother value")
        TestHelper._mkfile(test_dir + "centos-directory-1/cksum_testfile2.txt", "test successful")
        TestHelper._mkfile(test_dir + "centos-directory-1/subdir/testfile1.txt",
                           "test successful\nother value")
        TestHelper._mkfile(test_dir + "centos-directory-1/subdir/testfile2.txt", "test successful")

    @staticmethod
    def remove_file(path: str):
        cmd = ["rm", "-f", path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)

    @staticmethod
    def remove_dir(path: str):
        cmd = ["rm", "-rf", path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)

    @staticmethod
    def _mkdir(path: str):
        cmd = ["mkdir", path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)

    @staticmethod
    def _mkfile(path: str, content: str):
        subprocess.check_output('echo "' + content + '" > ' + path, universal_newlines=True, shell=True)

    @staticmethod
    def block_source_file(task):
        """Sets the directory/file at task source_path and all subdirectories to writeonly mode.
        
        :param task: the current task.
        """
        path = task.absolute_source_path
        if os.path.isdir(path):
            # we need to recurse into directories to make sure data is not changed during copy
            pathlist = task.get_source_dirlist()
            # reversed to block, else we could not write anymore
            pathlist.reverse()
            for full_path in pathlist:
                # 292 == S_IREAD|S_IRGRP|S_IROTH. On UNIX this is equivalent to chmod 444.
                os.chmod(full_path, 292)
            # task.set_data_writeblocked(True)
        elif os.path.isfile(path):
            os.chmod(path, 292)
            # task.set_data_writeblocked(True)
        else:
            task.add_exception(SourcePathNotValidException(Copytool.INVALID_SOURCE % (task.get_id(), path)))
            task.set_status(TaskStatus.EXCEPTION)
        return task

    @staticmethod
    def unblock_source_file(task):
        """Sets the directory/file at task source_path and all subdirectories to normal mode.
        
        :param task: the current task.
        """
        path = task.absolute_source_path
        if os.path.isdir(path):
            # we need to recurse into directories to make sure we can change everything afterwards
            pathlist = task.get_source_dirlist()
            # not reversd to unblock, to unlock sequencially
            for full_path in pathlist:
                # 493 ==  S_IRWXU|S_IROTH|S_IXOTH|S_IRGRP|S_IXGRP. On UNIX this is equivalent to chmod 755.
                os.chmod(full_path, 493)
            # task.set_data_writeblocked(False)
        elif os.path.isfile(path):
            os.chmod(path, 493)
            # task.set_data_writeblocked(False)
        else:
            task.add_exception(SourcePathNotValidException(Copytool.INVALID_SOURCE % (task.get_id(), path)))
            task.set_status(TaskStatus.EXCEPTION)
        return task

    @staticmethod
    def unblock_target_file(task):
        """Sets the directory/file at task target_path and all subdirectories to normal mode.
        
        :param task: the current task.
        """
        pathlist = task.get_target_dirlist()
        path = task.get_absolute_target_path()
        if os.path.isdir(path):
            # we need to recurse into directories to make sure we can change everything afterwards
            pathlist = task.get_source_dirlist()
            # not reversd to unblock, to unlock sequencially
            for full_path in pathlist:
                # 493 ==  S_IRWXU|S_IROTH|S_IXOTH|S_IRGRP|S_IXGRP. On UNIX this is equivalent to chmod 755.
                os.chmod(full_path, 493)
            # task.set_data_writeblocked(False)
        elif os.path.isfile(path):
            os.chmod(path, 493)
            # task.set_data_writeblocked(False)
        else:
            task.add_exception(SourcePathNotValidException(Copytool.INVALID_SOURCE % (task.get_id(), path)))
            task.set_status(TaskStatus.EXCEPTION)
        return task
