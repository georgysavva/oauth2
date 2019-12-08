import logging
from typing import Optional, Tuple

import requests

from apis import BaseAPIClient, APIError, IncorrectResponseError
from models import models

logger = logging.getLogger(__name__)

ERROR_CODE_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_CODE_ACCESS_TOKEN_EXPIRED = 'access_token_expired'


class AuthAPI(BaseAPIClient):
    def __init__(self, auth_api_base_url: str):
        super().__init__(auth_api_base_url)

    def get_access_token_info(self, access_token: str) -> models.AccessTokenInfo:
        url = self._build_full_url(endpoint='token')
        resp = requests.get(url, json={'access_token': access_token})
        # Further improvement: pass json schema to the base method,
        # to have automated data validation.
        response_json = self._process_response(resp)
        user_id, scope = self.validate_token_info_response(resp, response_json)
        return models.AccessTokenInfo(user_id, scope)

    @staticmethod
    def validate_token_info_response(response: requests.Response,
                                     response_json: dict) -> Tuple[str, list]:
        log_ctx = {'url': response.url, 'status_code': response.status_code,
                   'response_body': response_json}
        user_id = response_json.get('user_id')
        if not user_id or type(user_id) != str:
            logger.warning(
                "HTTP response body doesn't contain 'user_id' field or wrong type",
                extra=log_ctx
            )
            raise IncorrectResponseError("'user_id' field is missing or wrong type", response)
        scope = response_json.get('scope')
        if scope is None or type(scope) != list or any(type(item) != str for item in scope):
            logger.warning(
                "HTTP response body doesn't contain 'scope' field or wrong type",
                extra=log_ctx
            )
            raise IncorrectResponseError("'scope' field is missing or wrong type", response)

        return user_id, scope

    def _raise_error_if_necessary(self, response: requests.Response,
                                  response_json: Optional[dict]) -> None:
        if not response_json:
            return
        error_code = response_json.get('error')
        error_description = response_json.get('error_description')
        if error_code == ERROR_CODE_INVALID_ACCESS_TOKEN:
            raise InvalidAccessTokenError(error_description, response)
        if error_code == ERROR_CODE_ACCESS_TOKEN_EXPIRED:
            raise AccessTokenExpiredError(error_description, response)

        super()._raise_error_if_necessary(response, response_json)


class AuthorizationError(APIError):
    pass


class InvalidAccessTokenError(AuthorizationError):
    pass


class AccessTokenExpiredError(AuthorizationError):
    pass
