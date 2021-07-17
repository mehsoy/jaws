import os

import pytest
from unittest.mock import Mock

from worker.copytool.rsync import Rsync
from worker.copytool.shiftc import Shiftc
from worker.copytool.tar import Tar
from worker.msg_out import Out
from worker.storage import Storage
from worker.task import Task
from worker.worker_class import Worker


@pytest.fixture(scope='module')
def outStub():
    return Mock(spec=Out)


@pytest.fixture
def worker(outStub, storages):
    return Worker(worker_name='Worker1', msg_out=outStub, storages=storages)


@pytest.fixture(scope='module')
def default_rsync(outStub):
    return Rsync(1, outStub, '-asv --inplace', '/usr/bin/rsync')


@pytest.fixture(scope='module')
def default_tar(outStub):
    return Tar(1, outStub, '-H posix -p --no-ignore-command-error', '/bin/tar')


@pytest.fixture(scope='module')
def default_shiftc(outStub):
    return Shiftc(1, outStub, '', '/home/adrian/bin/shiftc')


@pytest.fixture(scope='module')
def config_path():
    return os.getcwd() + '/src/tests/worker/config_handling/conf.toml'


@pytest.fixture(scope='module')
def copytools_path():
    return os.getcwd() + '/src/tests/worker/config_handling/copytools.ini'


@pytest.fixture(scope='module')
def make_rsync_task(default_rsync, outStub):
    def _make_rsync_task(id: int, source: Storage, rel_path: str, target: Storage, msg_out=outStub):
        task = Task(id, source, rel_path, target, msg_out=msg_out)
        task.copytool = default_rsync
        return task

    return _make_rsync_task


@pytest.fixture(scope='module')
def make_tar_task(default_tar, outStub):
    def _make_tar_task(id, source, rel, target, msg_out=outStub):
        task = Task(id, source, rel, target, msg_out=msg_out)
        task.copytool = default_tar
        return task

    return _make_tar_task

@pytest.fixture(scope='module')
def make_shiftc_task(default_shiftc, outStub):
    def _make_shiftc_task(id, source, rel, target):
        task = Task(id, source, rel, target, msg_out=outStub)
        task.copytool = default_shiftc
        return task
    return _make_shiftc_task