# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import pytest


from unittest.mock import MagicMock, patch
from controller.app import create_app


@pytest.fixture
def application_adapter():
    with patch('application.application_adapter.Application') as mock:
        adapter = mock.return_value
        adapter.verify_user.return_value = json.dumps({'role' :'User'})
        adapter.create_job.return_value = json.dumps({'job_id': 5})
        yield adapter


def test_app(application_adapter):
    app = create_app()
    # initialize return values of application adapter
    app.config['ADAPTER'] = application_adapter()
    app.config['SERVER_ADDRESS'] = "141.52.39.127:3389"
    _host, _, _port = app.config.get('SERVER_ADDRESS').partition(':')
    _port = int(_port)
    app.run(host=_host, port=_port, use_reloader=False)

if __name__ == '__main__':
    test_app(application_adapter)


