from typing import Optional

import flask

import flaskapp
from apis.auth import AuthAPI
from apis.resource import ResourceAPI
from core import config
from flaskapp import views

"""
This module is responsible for all instances in the application using the configuration settings.
"""


def create_auth_api_client(
    auth_api_base_url: Optional[str] = None,
    client_id: Optional[str] = None, client_secret: Optional[str] = None,
    http_request_timeout: Optional[int] = None
) -> AuthAPI:
    auth_api_base_url = auth_api_base_url or config.AUTH_API_BASE_URL
    client_id = client_id or config.CLIENT_ID
    client_secret = client_secret or config.CLIENT_SECRET
    http_request_timeout = http_request_timeout or config.HTTP_REQUEST_TIMEOUT
    auth_api = AuthAPI(auth_api_base_url, client_id, client_secret, http_request_timeout)
    return auth_api


def create_resource_api_client(resource_api_base_url: Optional[str] = None,
                               http_request_timeout: Optional[int] = None) -> ResourceAPI:
    resource_api_base_url = resource_api_base_url or config.RESOURCE_API_BASE_URL
    http_request_timeout = http_request_timeout or config.HTTP_REQUEST_TIMEOUT
    resource_api = ResourceAPI(resource_api_base_url, http_request_timeout)
    return resource_api


def create_http_handler(auth_api: AuthAPI, resource_api: ResourceAPI) -> views.Handler:
    return views.Handler(auth_api, resource_api)


def create_wsgi() -> flask.Flask:
    auth_api = create_auth_api_client()
    resource_api = create_resource_api_client()
    http_handler = create_http_handler(auth_api, resource_api)
    return flaskapp.create_app(http_handler)
