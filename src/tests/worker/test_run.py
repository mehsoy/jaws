#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

import os

from mock import MagicMock
import pytest
from tests.worker.sleeptool import SleeperCopytool
from worker.run_thread import RunThread
from worker.storage import Storage

from worker.task_status import TaskStatus


@pytest.fixture
def sleeper_storage(outStub):
    storage = Storage('sleeper', '/mount/sleeper',
                      SleeperCopytool(1, outStub, 'sleep 20s;', ''),
                      '<dirname>-<username>-<number>', False)
    return storage


@pytest.mark.usefixtures('build_test_environment')
class TestRun:

    def test_run_shiftc(self, make_shiftc_task, dmd5, centos127, worker,
                           outStub):
        task = make_shiftc_task(1, centos127, 'johann-test_dir-1/', dmd5)
        task = worker.adopt_task(task)
        thread = RunThread(task, worker, outStub)
        thread.start()
        thread.join()
        assert task.status == TaskStatus.FINISHED
        assert os.path.isdir(task.absolute_target_path) is True
        abs_path = dmd5.mountpoint
        with open(abs_path + '/test_dir-johann-2/testfile1.txt') as f:
            assert f.read().rstrip() == 'test successful\nother value'
        assert os.path.exists(abs_path + '/test_dir-johann-2/subdir/testfile1.txt')
        assert not os.path.exists(task.absolute_source_path)

    def test_run_rsync(self, make_rsync_task, dmd5, centos127, worker,
                           outStub):
        task = make_rsync_task(1, dmd5, 'test_dir-johann-1/', centos127)
        task = worker.adopt_task(task)
        thread = RunThread(task, worker, outStub)
        thread.start()
        thread.join()
        assert task.status == TaskStatus.FINISHED
        assert os.path.isdir(task.absolute_target_path)
        assert os.path.isfile(task.absolute_target_path + '/dmd5file.txt')
        assert not os.path.exists(task.absolute_source_path)

    def test_run_tar(self, dmd5, archive1, worker, make_tar_task, outStub):
        # first compress
        task = make_tar_task(3, dmd5, 'test_dir-johann-1/', archive1, outStub)
        task = worker.adopt_task(task)
        thread1 = RunThread(task, worker, outStub)
        thread1.start()
        thread1.join()
        assert task.status == TaskStatus.FINISHED
        assert os.path.isdir(task.absolute_target_path)
        assert not os.path.exists(task.absolute_source_path)
        # now, extract
        task = make_tar_task(4, archive1, task.relative_target_path, dmd5)
        task = worker.adopt_task(task)
        thread2 = RunThread(task, worker, outStub)
        thread2.start()
        thread2.join()
        assert task.status == TaskStatus.FINISHED
        assert os.path.isdir(task.absolute_target_path)
        assert not os.path.exists(task.absolute_source_path)
        assert os.path.isfile(task.absolute_target_path + 'dmd5file.txt')

    @pytest.mark.skip()
    def test_cancel(self, dmd5, centos127, make_rsync_task, worker, outStub,
                    sleeper_storage):
        """Test if process killing works with a mocked copytools that sleeps
        for 20 seconds. """
        # TODO multithreading... idk
        task = make_rsync_task(7, dmd5, 'test_dir-johann-1/', sleeper_storage)
        # Since sleeper_storage is not mounted we need to mock the checks
        worker.verify_task_mountpoints = MagicMock(return_value=None)
        task = worker.adopt_task(task)
        thread = RunThread(task, worker, outStub)
        thread.start()
        # kill the process after 0.5 seconds
        time.sleep(2)
        taskkill = worker.cancel_task(task)
        assert taskkill.status == TaskStatus.TERMINATED
        thread.join()
        assert task.status == TaskStatus.TERMINATED
        assert task == taskkill
        assert task.copytool._process is None
