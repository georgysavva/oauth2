import logging

import jsonschema
from flask import request, jsonify

from flaskapp import app
import oauth2.exceptions

logger = logging.getLogger(__name__)

# Error code are from the oauth2 rfc:
# https://tools.ietf.org/html/rfc6749
ERROR_INVALID_REQUEST = 'invalid_request'
ERROR_INVALID_CLIENT = 'invalid_client'
ERROR_UNSUPPORTED_GRANT_TYPE = 'unsupported_grant_type'
ERROR_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_ACCESS_TOKEN_EXPIRED = 'access_token_expired'


class APIError(Exception):
    def __init__(self, message, error_code, status_code=400):
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


@app.route('/v1/token', methods=['POST'])
@app.jsonschema.validate('obtain_token_request')
def hello_world():
    request_data = request.json
    grant_type = request_data['grant_type']
    try:
        try:
            raise KeyError("fff")
        except:
            logger.exception('blablala %s', 'iii', extra={'oo': 2})
            pass
        logger.info('blablalallllllllllll %s', 'iii', extra={'oo': 2})

    except Exception as e:
        print(e)
        pass
    # AccessTokenManager(None).issue_token('fff', '', '', '', '')

    # if grant_type != models.GRANT_TYPE_PASSWORD:
    #     logger.warning(f"Token request has unsupported grant type: {grant_type}")
    # raise APIError()
    #     return error_response(
    #         ErrorCode.INVALID_REQUEST,
    #         error_description=f"Unsupported grant type. "
    #         f"Server only supports f{models.GrantType.PASSWORD.value} grant type."
    #     )
    # client_id = request_data['client_id']
    # client_secret = request_data['client_secret']
    # app_exists = models.Application.objects.filter(client_id=client_id,
    #                                                client_secret=client_secret).exists()
    # if not app_exists:
    #     self.logger.info(f"Invalid client credentials for client id: {client_id}")
    #     return error_response(
    #         ErrorCode.INVALID_CLIENT,
    #         f"Client with id {client_id} not found "
    #         f"or pair client_id and client_secret does not match"
    #     )
    # # We don't use username and password.
    # user = models.User.objects.first()
    # if not user:
    #     raise RuntimeError("We must have at least one user in db to operate")
    return 'fff'


@app.errorhandler(jsonschema.ValidationError)
def handle_error(error: jsonschema.ValidationError):
    logger.warning("Request schema validation failed", extra={'error': error.message})
    return error_response(ERROR_INVALID_REQUEST,
                          f"Request schema validation failed: {error.message}", 400)


@app.errorhandler(APIError)
def handle_error(error: APIError):
    return error_response(error.error_code, str(error), error.status_code)


@app.errorhandler(oauth2.exceptions.InvalidClientError)
def handle_error(error: oauth2.exceptions.InvalidClientError):
    return error_response(ERROR_INVALID_CLIENT, str(error), 400)


@app.errorhandler(oauth2.exceptions.UnsupportedGrantTypeError)
def handle_error(error: oauth2.exceptions.UnsupportedGrantTypeError):
    return error_response(ERROR_UNSUPPORTED_GRANT_TYPE, str(error), 400)


@app.errorhandler(oauth2.exceptions.InvalidAccessTokenError)
def handle_error(error: oauth2.exceptions.InvalidAccessTokenError):
    return error_response(ERROR_INVALID_ACCESS_TOKEN, str(error), 401)


@app.errorhandler(oauth2.exceptions.ExpiredAccessTokenError)
def handle_error(error: oauth2.exceptions.ExpiredAccessTokenError):
    return error_response(ERROR_ACCESS_TOKEN_EXPIRED, str(error), 401)


def error_response(error_code: str, error_description: str, status_code: int = 400):
    return jsonify({'error': error_code, 'error_description': error_description}), status_code
