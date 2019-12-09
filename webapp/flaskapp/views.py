import logging

from flask import Flask

import apis.resource
from apis.auth import AuthAPI
from apis.resource import ResourceAPI

logger = logging.getLogger(__name__)


# Further improvement: Move business logic to a separate class (Service),
# that knows nothing about http transport layer and flask
# As it done in oauth2_server and resource_server projects
# But since it's not a real web application and the logic layer is really thin,
# it's ok to put it here.
class Handler:
    def __init__(self, auth_api: AuthAPI, resource_api: ResourceAPI):
        self._auth_client = auth_api
        self._resource_api = resource_api

    def get_current_time(self):
        access_token = self._get_access_token()
        logger.info("Requesting current time resource")
        result = self._resource_api.get_current_time(access_token)
        logger.info("Resource current time obtained", extra={'current_time': result})
        return result + '\n'

    def get_epoch_time(self):
        access_token = self._get_access_token()
        logger.info("Requesting epoch time resource")
        result = self._resource_api.get_epoch_time(access_token)
        logger.info("Resource epoch time obtained", extra={'epoch_time': result})
        return str(result) + '\n'

    def _get_access_token(self) -> str:
        grant_type = 'password'
        username = 'bob'
        logger.info(
            "Requesting access token from the oauth2 server",
            extra={'grant_type': grant_type, 'username': username}
        )
        access_token = self._auth_client.request_access_token(grant_type, username,
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
    flask_app.errorhandler(apis.resource.ResourceAuthorizationError)(
        handle_resource_authorization_error)


# For now we show the error message as is.
# Without translating it in something that would non-technical user understands.
def handle_resource_authorization_error(error: apis.resource.ResourceAuthorizationError):
    logger.warning("Resource server authorization failed", extra={'error': error})
    return str(error) + '\n', 403 if isinstance(error, apis.resource.PermissionDeniedError) else 401
