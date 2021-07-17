#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path

import pytest

from worker.action import Action
from worker.copytool.rsync import Rsync
from worker.task_status import TaskStatus


@pytest.fixture
def rsync_output():
    return '''
    Number of files: 20 (reg: 10, dir: 10)
    Number of created files: 0
    Number of deleted files: 0
    Number of regular files transferred: 10
    Total file size: 115,909 bytes
    Total transferred file size: 115,909 bytes
    Literal data: 0 bytes
    Matched data: 0 bytes
    File list size: 0
    File list generation time: 0.008 seconds
    File list transfer time: 0.000 seconds
    Total bytes sent: 600
    Total bytes received: 21

    sent 600 bytes  received 21 bytes  1,242.00 bytes/sec
    total size is 115,909  speedup is 186.65
    '''


@pytest.mark.usefixtures('build_test_environment')
class TestRsync:

    def test_recursive(self, centos127, dmd5, make_rsync_task):
        task = make_rsync_task(1, centos127, 'johann-test_dir-1/', dmd5)
        task.copytool.copy(task)

        abs_path = dmd5.mountpoint
        assert os.path.isdir(task.absolute_target_path) is True
        assert task.status == TaskStatus.COPIED
        with open(abs_path + '/test_dir-johann-2/testfile1.txt') as f:
            assert f.read().rstrip() == 'test successful\nother value'
        assert os.path.exists(abs_path + '/test_dir-johann-2/subdir/testfile1.txt')


def test_action_support(default_rsync):
    assert default_rsync.supports(Action.COPY)


def test_get_list_of_numbers(rsync_output):
    lines = rsync_output.split('\n')
    numbers = Rsync._get_list_of_numbers(lines[1])
    assert numbers == [20, 10, 10]

    numbers = Rsync._get_list_of_numbers(lines[3])
    assert numbers == [0]

    numbers = Rsync._get_list_of_numbers(lines[6])
    assert numbers == [115909]

    numbers = Rsync._get_list_of_numbers(lines[11])
    assert numbers == [0]

    numbers = Rsync._get_list_of_numbers(lines[16])
    assert numbers == [600, 21, 1242]


def test_parse_output(rsync_output):
    stats = Rsync.parse_stats(rsync_output)
    assert stats == dict(n_of_files=20, n_of_dirs=10, total_size=115909)
