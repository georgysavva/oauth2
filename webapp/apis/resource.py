import logging
from typing import Optional

import requests

from apis import BaseAPIClient, IncorrectResponseError, APIError

logger = logging.getLogger(__name__)

ERROR_CODE_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_CODE_ACCESS_TOKEN_EXPIRED = 'access_token_expired'
ERROR_CODE_PERMISSION_DENIED = 'permission_denied'


class ResourceAPI(BaseAPIClient):
    def __init__(self, resource_api_base_url: str):
        super().__init__(resource_api_base_url)

    def get_current_time(self, access_token: str) -> str:
        url = self._build_full_url(endpoint='current_time')
        resp = requests.get(url, headers=self._build_bearer_header(access_token))

        # Further improvement: pass json schema to the base method,
        # to have automated data validation.
        # Now we have only one field so we can check it manually.
        response_json = self._process_response(resp)
        current_time = response_json.get('current_time')
        if not current_time or type(current_time) != str:
            logger.warning(
                "HTTP json body doesn't contain 'current_time' field or wrong type",
                extra={'url': resp.url, 'status_code': resp.status_code,
                       'response_body': response_json}
            )
            raise IncorrectResponseError("'current_time' field is missing or wrong type", resp)
        return current_time

    def get_epoch_time(self, access_token: str) -> int:
        url = self._build_full_url(endpoint='epoch_time')
        resp = requests.get(url, headers=self._build_bearer_header(access_token))

        # Further improvement: pass json schema to the base method,
        # to have automated data validation.
        # Now we have only one field so we can check it manually.
        response_json = self._process_response(resp)
        epoch_time = response_json.get('epoch_time')
        if not epoch_time or type(epoch_time) != int:
            logger.warning(
                "HTTP json body doesn't contain 'epoch_time' field or wrong type",
                extra={'url': resp.url, 'status_code': resp.status_code,
                       'response_body': response_json}
            )
            raise IncorrectResponseError("'epoch_time' field is missing or wrong type", resp)
        return epoch_time

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
        if error_code == ERROR_CODE_PERMISSION_DENIED:
            raise PermissionDeniedError(error_description, response)

        super()._raise_error_if_necessary(response, response_json)

    @staticmethod
    def _build_bearer_header(access_token: str) -> dict:
        return {'Authorization': f'Bearer {access_token}'}


class ResourceAuthorizationError(APIError):
    pass


class InvalidAccessTokenError(ResourceAuthorizationError):
    pass


class AccessTokenExpiredError(ResourceAuthorizationError):
    pass


class PermissionDeniedError(ResourceAuthorizationError):
    pass
