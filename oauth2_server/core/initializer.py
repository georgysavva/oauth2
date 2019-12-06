from typing import List, Optional

import flask

import flaskapp
from core import config
from flaskapp import views
from inmem_storage.applications import InMemApplicationsRepo
from models import models
from oauth2.service import Oauth2Service


def create_applications_repository(
    default_apps: Optional[List[dict]] = None) -> InMemApplicationsRepo:
    default_apps = default_apps or config.DEFAULT_OAUTH_APPLICATIONS
    apps_repo = InMemApplicationsRepo().create_default_apps(default_apps)
    return apps_repo


def create_oauth2_service(
    applications_repo: models.ApplicationsRepository,
    default_users_scope: Optional[List[str]] = None, issuer_url: Optional[str] = None,
    jwt_secret_key: Optional[str] = None, access_token_lifetime: Optional[int] = None
) -> Oauth2Service:
    default_users_scope = default_users_scope or config.DEFAULT_USERS_SCOPE
    issuer_url = issuer_url or config.ISSUER_URL
    jwt_secret_key = jwt_secret_key or config.JWT_SECRET_KEY
    access_token_lifetime = access_token_lifetime or config.ACCESS_TOKEN_LIFETIME
    service = Oauth2Service(
        applications_repo, default_users_scope, issuer_url, jwt_secret_key, access_token_lifetime
    )
    return service


def create_http_handler(
    oauth2_service: Oauth2Service) -> views.AuthorizationHandler:
    return views.AuthorizationHandler(oauth2_service)


def create_wsgi() -> flask.Flask:
    applications_repo = create_applications_repository()
    oauth2_service = create_oauth2_service(applications_repo)
    http_handler = create_http_handler(oauth2_service)
    return flaskapp.create_app(http_handler)
