import logging

import flask_jsonschema
import jsonschema
from flask import request, jsonify, Flask

from oauth2 import exceptions
from oauth2.service import Oauth2Service

"""
This module is responsible for working with http transport layer. 
It parses and validates http request data and serializes data from the business logic layer.
"""

logger = logging.getLogger(__name__)

# Error code are from the oauth2 rfc:
# https://tools.ietf.org/html/rfc6749
ERROR_INVALID_REQUEST = 'invalid_request'
ERROR_INVALID_CLIENT = 'invalid_client'
ERROR_UNSUPPORTED_GRANT_TYPE = 'unsupported_grant_type'
ERROR_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_ACCESS_TOKEN_EXPIRED = 'access_token_expired'


class AuthorizationHandler:
    def __init__(self, oauth2_service: Oauth2Service):
        self._oauth2_service = oauth2_service

    @flask_jsonschema.validate('issue_token_request')
    def issue_token(self):
        request_data = request.json
        access_token = self._oauth2_service.issue_token(
            request_data['grant_type'], request_data['client_id'],
            request_data['client_secret'], request_data['username']
        )
        return jsonify({'access_token': access_token})

    @flask_jsonschema.validate('get_token_info_request')
    def get_token_info(self):
        request_data = request.json
        token_info = self._oauth2_service.get_token_info(request_data['access_token'])
        return jsonify({
            'user_id': token_info.user_id,
            'client_id': token_info.client_id,
            'issuer_url': token_info.issuer_url,
            'issued_at': token_info.issued_at,
            'expires_at': token_info.expires_at,
            'scope': token_info.scope
        })

    def register_routes(self, flask_app: Flask) -> None:
        flask_app.add_url_rule(
            '/v1/token', methods=['POST'], view_func=self.issue_token
        )
        flask_app.add_url_rule(
            '/v1/token', methods=['GET'], view_func=self.get_token_info
        )


def register_error_handlers(flask_app: Flask) -> None:
    flask_app.errorhandler(jsonschema.ValidationError)(handle_json_validation_error)
    flask_app.errorhandler(exceptions.InvalidClientError)(handle_invalid_client)
    flask_app.errorhandler(exceptions.UnsupportedGrantTypeError)(handle_unsupported_grant_type)
    flask_app.errorhandler(exceptions.InvalidAccessTokenError)(handle_invalid_access_token)
    flask_app.errorhandler(exceptions.AccessTokenExpiredError)(handle_expired_access_token)


def handle_json_validation_error(error: jsonschema.ValidationError):
    error_details = str(error)
    logger.warning("Request schema validation failed", extra={'error': error_details})
    return error_response(ERROR_INVALID_REQUEST,
                          f"Request schema validation failed: {error_details}", 400)


def handle_invalid_client(error: exceptions.InvalidClientError):
    return error_response(ERROR_INVALID_CLIENT, str(error), 400)


def handle_unsupported_grant_type(error: exceptions.UnsupportedGrantTypeError):
    return error_response(ERROR_UNSUPPORTED_GRANT_TYPE, str(error), 400)


def handle_invalid_access_token(error: exceptions.InvalidAccessTokenError):
    return error_response(ERROR_INVALID_ACCESS_TOKEN, str(error), 401)


def handle_expired_access_token(error: exceptions.AccessTokenExpiredError):
    return error_response(ERROR_ACCESS_TOKEN_EXPIRED, str(error), 401)


def error_response(error_code: str, error_description: str, status_code: int = 400):
    return jsonify({'error': error_code, 'error_description': error_description}), status_code
