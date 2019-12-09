from flask import Flask

from flaskapp import views


def create_app(http_handler: views.Handler) -> Flask:
    """
    Bound http layer class (handler) to the new flask application
    """
    app = Flask(__name__)
    http_handler.register_routes(app)
    views.register_error_handlers(app)
    return app
