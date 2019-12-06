from typing import Optional

import flask

import flaskapp
from apis.auth import AuthAPI
from core import config
from flaskapp import views
from timer.service import TimerService


def create_auth_api_client(auth_api_base_url: Optional[str] = None) -> AuthAPI:
    auth_api_base_url = auth_api_base_url or config.AUTH_API_BASE_URL
    auth_api = AuthAPI(auth_api_base_url)
    return auth_api


def create_timer_service(auth_api: AuthAPI) -> TimerService:
    timer_service = TimerService(auth_api)
    return timer_service


def create_http_handler(timer_service: TimerService) -> views.Handler:
    return views.Handler(timer_service)


def create_wsgi() -> flask.Flask:
    auth_api = create_auth_api_client()
    timer_service = create_timer_service(auth_api)
    http_handler = create_http_handler(timer_service)
    return flaskapp.create_app(http_handler)
