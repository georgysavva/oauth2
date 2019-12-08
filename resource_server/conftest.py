import pytest

from core import initializer


@pytest.fixture
def flask_client():
    flask_app = initializer.create_wsgi()
    flask_app.config['TESTING'] = True
    client = flask_app.test_client()
    return client
