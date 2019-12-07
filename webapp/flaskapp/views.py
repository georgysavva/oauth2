import logging

from flask import Flask

from apis import exceptions
from apis.auth import AuthAPI
from apis.resource import ResourceAPI

logger = logging.getLogger(__name__)


class Handler:
    def __init__(self, auth_api: AuthAPI, resource_api: ResourceAPI):
        self._auth_client = auth_api
        self._resource_api = resource_api

    def get_current_time(self):
        access_token = self._get_access_token()
        result = self._resource_api.get_current_time(access_token)
        return result

    def get_epoch_time(self):
        access_token = self._get_access_token()
        result = self._resource_api.get_epoch_time(access_token)
        return result

    def _get_access_token(self) -> str:
        access_token = self._auth_client.request_access_token(grant_type='password', username='bob',
                                                              password='bob-pass')
        return access_token

    def register_routes(self, flask_app: Flask) -> None:
        flask_app.add_url_rule(
            '/current_time', methods=['GET'], view_func=self.get_current_time
        )
        flask_app.add_url_rule(
            '/epoch_time', methods=['GET'], view_func=self.get_epoch_time
        )


def register_error_handlers(flask_app: Flask) -> None:
    flask_app.errorhandler(exceptions.AccessTokenExpiredError)(handle_access_token_expired)
    flask_app.errorhandler(exceptions.PermissionDeniedError)(handle_permission_denied)


# For now we show the error message as is.
# Without translating it in something that would non-technical user understands.
def handle_access_token_expired(error: exceptions.AccessTokenExpiredError):
    return str(error), 401


def handle_permission_denied(error: exceptions.PermissionDeniedError):
    return str(error), 403
