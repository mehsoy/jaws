import pytest
import json
from unittest.mock import MagicMock, patch

from controller.app import create_app

@pytest.fixture
def params():
    d = dict(
        data=json.dumps(dict(source='storage1',target='storage2')),
        cookie = {
            'user':'user1',
            'token':'tokem1'
        })
    return d

@pytest.fixture
def application_adapter(params):
    with patch('application.application_adapter.Application') as mock:
        adapter = mock.return_value
        adapter.verify_user.return_value = json.dumps(dict(role='Administrator'))
        adapter.create_job.return_value = json.dumps(dict(job_id=5))
        yield adapter
        #Put this in test_'s bottom part?
        adapter.verify_user.assert_called_with(json.dumps(params['cookie']))
        adapter.create_job.assert_called_with(params['data'])

@pytest.fixture(scope='function')
def test_app(application_adapter):
    app = create_app()
    #initialize return values of application adapter
    app.config['ADAPTER'] = application_adapter
    app.testing= True
    with app.test_client() as app:
        yield app

def test_job_creation(test_app, params):
    response = test_app.post('/api/jobs/', headers={'Set-Cookies':params['cookie']}, data=params['data'], content_type='application/json')
    assert response.data == json.dumps(dict(job_id=5))
