""".. module:: app """
from controller import unmunge_request, munge_response, extract_action_log
from controller.controller_mailbox import ControllerMailbox

from flask import Flask
from flask_socketio import SocketIO
from configparser import ConfigParser

from application.application_adapter import Application
from controller.blueprints.api import blueprint as api

from controller.blueprints.web_app import ns as web_app


socketio = SocketIO()
mailbox = ControllerMailbox(socketio)


@socketio.on('client_connected', namespace='/web/admin/dashboard')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    mailbox.update_worker(1)


def create_app(config_path):
    """
    Factory pattern to create different app instances. Currently only
    supports INI files as input. """
    app = Flask(__name__, template_folder="blueprints/templates", static_folder="blueprints/static")

    app.register_blueprint(api)
    app.register_blueprint(web_app)
    app.before_request(unmunge_request)
    app.before_request(extract_action_log)
    app.after_request(munge_response)
    config = ConfigParser()
    config.read(config_path)
    app.config['DEBUG'] = config.get('flask', 'DEBUG')
    app.config['SERVER_ADDRESS'] = config.get('flask', 'SERVER_ADDRESS')
    app.config['ERROR_INCLUDE_MESSAGE'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    app.config['APPLICATION'] = Application(controller_mailbox=mailbox)

    socketio.init_app(app)

    #    set_error_handlers(app)
    return app


#def set_error_handlers(app):
#    @app.errorhandler(400)
#    def bad_request(e):
#        tb = traceback.format_exc()
#        resp = dict(message=tb)
#        return make_response(jsonify(resp), 400)
#
#    @app.errorhandler(500)
#    def inter_error_handler(e):
#        return make_response(jsonify(e), 500) 
