import sys
import json
from unittest.mock import MagicMock, patch
import pytest

from application.application_adapter import Application
from controller.app import create_app
from views.CmdView.command_line import CommandLine


@pytest.fixture
def flask_app():
    app = create_app()
    app.config['ADAPTER'] = Application()
    app.testing= True
    return app.test_client()

def test_job_creation(flask_app, adapter,capfd):
    with patch('application_adapter.Application') as mock:
        adapter = mock.return_value
        adapter.create_job.return_value = json.dumps({ 'job_id': 5 })
        adapter.verify_user.return_value = 'Administrator'
        cookies = {
            'username': 'user1',
            'token': 'tokem1'
            },
        body = {
            'source': 'storage1',
            'target': 'storage2',
            }

        sys.argv = ['dmd', 'move', 'storage1', 'storage2']
        CommandLine().process()
        out,err = capfd.readouterr()

        adapter.verify_user.assert_called_once_with(json.dumps(cookies))
        adapter.create_job.assert_called_once_with(json.dumps(body))
        assert out == '{ \'job_id\': 5 }'
