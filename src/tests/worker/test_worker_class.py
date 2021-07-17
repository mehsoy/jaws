import os

import pytest

from worker.task_status import TaskStatus
from worker.worker_class import Worker
from worker.worker_status import WorkerStatus



@pytest.mark.usefixtures('build_test_environment')
class TestWorker:

    def test_adopt_task(self, centos127, archive1, make_tar_task, worker):
        task = make_tar_task(1, centos127, 'johann-test_dir-1/', archive1)
        worker.adopt_task(task)
        assert worker.status == WorkerStatus.ACTIVE
        assert task.status == TaskStatus.INITIALIZED
        worker._msg.update_status.assert_called_once_with(new_status=WorkerStatus.ACTIVE)

    def test_copy_task(self, centos127, archive1, make_tar_task, worker):
        task = make_tar_task(1, centos127, 'johann-test_dir-1/', archive1)
        worker.adopt_task(task)
        worker.copy(task)
        assert os.path.exists(task.absolute_target_path)
        assert task.status == TaskStatus.COPIED
