#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import subprocess

from worker.task_status import TaskStatus
from worker.copytool.copytool import Copytool
from exceptions.source_path_not_valid_exception import SourcePathNotValidException

base_dir = '/mount/'

@pytest.fixture
def build_test_environment(centos127, dmd5, archive1):
    # build file structure for centos
    test_dir = centos127.mountpoint
    _mkdir(test_dir + "johann-directory-1")
    _mkdir(test_dir + "johann-directory-1/subdir")
    _mkdir(test_dir + "johann-test_dir-1")
    _mkdir(test_dir + "johann-test_dir-1/subdir")
    _mkdir(test_dir + "moved")
    _mkdir(test_dir + "extract")

    _mkfile(test_dir + "johann-testfile-1.txt", "test successful\nother value")
    _mkfile(test_dir + "johann-test_dir-1/testfile1.txt", "test successful\nother value")
    _mkfile(test_dir + "johann-test_dir-1/testfile2.txt", "test successful")
    _mkfile(test_dir + "johann-test_dir-1/subdir/testfile1.txt",
            "test successful\nother value")
    _mkfile(test_dir + "johann-test_dir-1/subdir/testfile2.txt", "test successful")

    _mkfile(test_dir + "johann-directory-1/cksum_testfile1.txt", "test successful\nother value")
    _mkfile(test_dir + "johann-directory-1/cksum_testfile2.txt", "test successful")
    _mkfile(test_dir + "johann-directory-1/subdir/testfile1.txt",
            "test successful\nother value")
    _mkfile(test_dir + "johann-directory-1/subdir/testfile2.txt", "test successful")

    # build file structure for dmd5
    test_dir = dmd5.mountpoint

    # build file structure for archive1
    test_dir = archive1.mountpoint

    yield

    for storage in [centos127, archive1, dmd5]:
        remove_subdirs(storage.mountpoint)


def remove_file(path: str):
    cmd = ["rm", "-f", path]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)


def remove_subdirs(path: str):
    cmd = ["rm", "-rf", path + '/*']
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)


def _mkdir(path: str):
    cmd = ["mkdir", path]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)


def _mkfile(path: str, content: str):
    subprocess.check_output('echo "' + content + '" > ' + path, universal_newlines=True, shell=True)
