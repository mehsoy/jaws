import pytest

from worker.worker_initializer import WorkerInitializer


@pytest.fixture
def wi(config_path, copytools_path):
    wi = WorkerInitializer(config_path, copytools_path)
    return wi


def test_created_storages(wi, archive1, centos127):
    storages = wi._storages
    assert storages['archive1'].mountpoint == archive1.mountpoint
    assert storages['archive1'].get_naming_convention() == archive1.get_naming_convention()
    assert storages['archive1']._is_archive is True

    assert storages['centos'].mountpoint == centos127.mountpoint
    assert storages['centos'].get_naming_convention() == centos127.get_naming_convention()
    assert storages['centos']._is_archive is False

    assert storages['archive1'].get_copytool()._executable_path == '/bin/tar'
