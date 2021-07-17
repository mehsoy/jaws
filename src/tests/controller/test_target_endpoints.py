import pytest
import json
from unittest.mock import MagicMock, patch
from werkzeug.http import dump_cookie

from controller.app import create_app

@pytest.fixture
def params():
    d = dict(
        target_list=json.dumps(dict(targets=['target1','target2'])),
        cookie = {
            'username':'user1',
            'token':'tokem1'
        })
    return d

@pytest.fixture
def application_adapter(params):
    with patch('application.application_adapter.Application') as mock:
        adapter = mock.return_value
        adapter.verify_user.return_value = json.dumps(dict(role='Administrator'))
        adapter.get_target_list.return_value = params['target_list']
        yield adapter
        #Put this in test_'s bottom part?
        adapter.verify_user.assert_called_with(json.dumps(params['cookie']))
        adapter.get_target_list.assert_called_with()

@pytest.fixture(scope='function')
def test_app(application_adapter):
    app = create_app()
    #initialize return values of application adapter
    app.config['ADAPTER'] = application_adapter
    app.testing=True
    with app.test_client() as app:
        yield app

def test_target_list(test_app, params):
    response = test_app.get('/api/targets/', headers=dump_cookie(params['cookie']), content_type='application/json')
    #jsonify is called with MagickMock object as parameter in target_endpoints,
    #which results in this response returning system intern error (as string)
    assert response.data == params['target_list']
