import os

import flask_jsonschema
from flask import Flask

import paths
from flaskapp import views

FLASK_APP_DIR = os.path.join(paths.BASE_DIR, 'flaskapp')


def create_app(http_handler: views.AuthorizationHandler) -> Flask:
    app = Flask(__name__)
    app.config['JSONSCHEMA_DIR'] = os.path.join(FLASK_APP_DIR, 'json_schemas')
    flask_jsonschema.JsonSchema(app)
    http_handler.register_routes(app)
    views.register_error_handlers(app)
    return app
