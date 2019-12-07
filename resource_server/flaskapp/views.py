import logging

from flask import Flask, jsonify, request

from timer.service import TimerService
from apis.exceptions import InvalidAccessTokenError, AccessTokenExpiredError
from timer.exceptions import PermissionDeniedError

logger = logging.getLogger(__name__)

ERROR_INVALID_REQUEST = 'invalid_request'
ERROR_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_ACCESS_TOKEN_EXPIRED = 'access_token_expired'
ERROR_PERMISSION_DENIED = 'permission_denied'


class BadAuthorizationHeader(Exception):
    pass


class Handler:
    def __init__(self, timer_service: TimerService):
        self._timer_service = timer_service

    def get_current_time(self):
        access_token = self._retrieve_token_from_headers()
        current_time = self._timer_service.get_current_time(access_token)
        return jsonify({'current_time': current_time.isoformat()})

    def get_epoch_time(self):
        access_token = self._retrieve_token_from_headers()
        epoch_time = self._timer_service.get_epoch_time(access_token)
        return jsonify({'epoch_time': epoch_time})

    @staticmethod
    def _retrieve_token_from_headers() -> str:
        header = request.headers.get('Authorization')
        if not header:
            raise BadAuthorizationHeader("Authorization header is missing")
        if not header.startswith('Bearer '):
            raise BadAuthorizationHeader(
                "Authorization header has invalid format: it must start with 'Bearer")
        return header[len('Bearer '):]

    def register_routes(self, flask_app: Flask) -> None:
        flask_app.add_url_rule(
            '/v1/current_time', methods=['GET'], view_func=self.get_current_time
        )
        flask_app.add_url_rule(
            '/v1/epoch_time', methods=['GET'], view_func=self.get_epoch_time
        )


def register_error_handlers(flask_app: Flask) -> None:
    flask_app.errorhandler(InvalidAccessTokenError)(handle_invalid_access_token)
    flask_app.errorhandler(AccessTokenExpiredError)(handle_access_token_expired)
    flask_app.errorhandler(PermissionDeniedError)(handle_permission_denied)
    flask_app.errorhandler(BadAuthorizationHeader)(handle_bad_authorization_header)


def handle_invalid_access_token(error: InvalidAccessTokenError):
    return error_response(ERROR_INVALID_ACCESS_TOKEN, str(error), 401)


def handle_access_token_expired(error: AccessTokenExpiredError):
    return error_response(ERROR_ACCESS_TOKEN_EXPIRED, str(error), 401)


def handle_permission_denied(error: PermissionDeniedError):
    return error_response(ERROR_PERMISSION_DENIED, str(error), 403)


def handle_bad_authorization_header(error: BadAuthorizationHeader):
    return error_response(ERROR_INVALID_REQUEST, str(error), 400)


def error_response(error_code: str, error_description: str, status_code: int = 400):
    return jsonify({'error': error_code, 'error_description': error_description}), status_code
