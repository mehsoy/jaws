""".. module:: controller_initializer """
from controller.app import create_app, socketio


class ControllerInitializer:
    
    def __init__(self, config_path):
        app = create_app(config_path)

        _host, _, _port = app.config.get('SERVER_ADDRESS').partition(':')
        _port = int(_port)

        socketio.run(app=app, host=_host, port=_port, use_reloader=False, debug=False)

