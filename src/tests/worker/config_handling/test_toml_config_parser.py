import os
import pytest
import toml
from voluptuous import MultipleInvalid

from worker.conf_schemata import validate_general, validate_storage


def test_toml_loader():
    config_dict = toml.load(os.getcwd() + '/src/tests/worker/config_handling/conf.toml')
    validate_general(config_dict['general'])
    validate_storage(config_dict['archive1'])

    assert config_dict['archive1']['copytool']['copytool'] == 'tar'
    assert config_dict['archive1']['copytool']['gzip'] is True
    assert config_dict['archive1']['copytool']['retrycount'] == 0
    assert config_dict['archive1']['type'] == 'archive'


def test_corrupted_toml_loader():
    config_dict = toml.load(os.getcwd() + '/src/tests/worker/config_handling/corrupted_conf.toml')
    with pytest.raises(MultipleInvalid):
        validate_general(config_dict['general'])
    with pytest.raises(MultipleInvalid):
        validate_storage(config_dict['archive1'])
