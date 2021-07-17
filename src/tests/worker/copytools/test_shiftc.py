#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path

import pytest

from exceptions.naming_convention_error import NamingConventionError
from worker.copytool.shiftc import Shiftc
from worker.task_status import TaskStatus

@pytest.fixture
def shiftc_output():
    return '''File::Glob::glob() will disappear in perl 5.30. Use File::Glob::bsd_glob() 
    instead. at /home/adrian/bin/shiftc line 274.
    Shift id is 284
    Waiting for transfer to complete...

     id | state |  dirs | files |   file size |  date |  run |   rate
        |       |  sums | attrs |    sum size |  time | left |
    ----+-------+-------+-------+-------------+-------+------+-------
    284 | done  | 10/10 | 10/10 | 116KB/116KB | 12/23 |   2s | 58KB/s
        |       |   0/0 | 20/20 |   0.0B/0.0B | 19:21 |      |
    '''


def test_parse_stats(shiftc_output):
    # Files and Directories are disjunct in the shiftc output
    stats = Shiftc.parse_stats(shiftc_output)
    assert stats['n_of_files'] == 20
    assert stats['n_of_dirs'] == 10
    assert stats['total_size'] == 116_000


@pytest.mark.usefixtures('build_test_environment')
class TestShiftc:

    def test_copy(self, centos127, dmd5, make_shiftc_task):
        task = make_shiftc_task(1, centos127, 'johann-test_dir-1/', dmd5)
        task.copytool.copy(task)
        # again ... see below
        import time
        time.sleep(1)

        abs_path = dmd5.mountpoint
        assert os.path.isdir(task.absolute_target_path) is True
        assert task.status == TaskStatus.COPIED
        with open(abs_path + '/test_dir-johann-2/testfile1.txt') as f:
            assert f.read().rstrip() == 'test successful\nother value'
        assert os.path.exists(abs_path + '/test_dir-johann-2/subdir/testfile1.txt')


    def test_directory_compress(self, centos127, archive1, make_shiftc_task):
        task = make_shiftc_task(1, centos127, 'johann-test_dir-1/', archive1)
        task.copytool.copy(task)
        assert os.path.exists(task.absolute_target_path) is True
        assert task.status == TaskStatus.COPIED

        task = task.copytool.consistency_check(task)
        assert task.status == TaskStatus.CHECKED

    def test_directory_extract(self, centos127, archive1, make_shiftc_task):
        task = make_shiftc_task(1, archive1, 'johann-secret_archive-1/', centos127)
        task = task.copytool.copy(task)
        # TODO we need sleep otherwise assertion kicks in too quickly. Need better solution.
        # throws error in real application, cause source is deleted too quickly for shiftc
        import time
        time.sleep(1)

        abs_path = task.absolute_target_path
        assert task.status == TaskStatus.COPIED
        assert os.path.exists(abs_path + 'bible/jesus.txt')
        assert os.path.exists(abs_path + 'bible/maria.rc')
        with open(abs_path + 'bible/jesus.txt', 'r') as f:
            assert f.read().rstrip() == 'Let there be light.'

    def test_bad_naming(self, centos127, archive1, make_shiftc_task):
        task = make_shiftc_task(1, centos127, 'bad_naming', archive1)
        with pytest.raises(NamingConventionError):
            task.copytool.copy(task)