import os

import pytest

from worker.config_handler import ConfigHandler


@pytest.fixture(scope='module')
def config_handler(config_path):
    config_handler = ConfigHandler(config_path)
    return config_handler


def test_general_config(config_handler):
    assert config_handler.get_worker_name() == 'worker1'
    assert config_handler.get_authentification_token() == 'secret01'


def test_storages(archive1, centos127, dmd5, config_handler):
    storages = config_handler.get_storages()

    assert storages['archive1']['type'] == 'archive'
    assert storages['archive1']['copytool']['retrycount'] == 0

    assert storages['centos']['type'] == 'posix'

    assert storages['dmd5']['type'] == 'posix'
    assert storages['dmd5']['copytool']['retrycount'] == 1
