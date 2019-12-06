from typing import Optional

import flask

import flaskapp
from apis.auth import AuthAPI
from apis.resource import ResourceAPI
from core import config
from flaskapp import views


def create_auth_api_client(
    auth_api_base_url: Optional[str] = None,
    client_id: Optional[str] = None, client_secret: Optional[str] = None
) -> AuthAPI:
    auth_api_base_url = auth_api_base_url or config.AUTH_API_BASE_URL
    client_id = client_id or config.CLIENT_ID
    client_secret = client_secret or config.CLIENT_SECRET
    auth_api = AuthAPI(auth_api_base_url, client_id, client_secret)
    return auth_api


def create_resource_api_client(resource_api_base_url: Optional[str] = None) -> ResourceAPI:
    resource_api_base_url = resource_api_base_url or config.RESOURCE_API_BASE_URL
    resource_api = ResourceAPI(resource_api_base_url)
    return resource_api


def create_http_handler(auth_api: AuthAPI, resource_api: ResourceAPI) -> views.Handler:
    return views.Handler(auth_api, resource_api)


def initialize_wsgi() -> flask.Flask:
    auth_api = create_auth_api_client()
    resource_api = create_resource_api_client()
    http_handler = create_http_handler(auth_api, resource_api)
    return flaskapp.create_app(http_handler)
