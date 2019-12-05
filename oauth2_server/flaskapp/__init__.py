import flask_jsonschema
from flask import Flask

import paths
from flaskapp import views


def create_app(authorization_handler: views.AuthorizationHandler) -> Flask:
    app = Flask(__name__)
    app.config['JSONSCHEMA_DIR'] = paths.JSON_SCHEMAS_DIR
    flask_jsonschema.JsonSchema(app)
    authorization_handler.register_routes(app)
    views.register_error_handlers(app)
    return app
