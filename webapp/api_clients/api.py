from typing import Optional

import requests
from api_clients import BaseAPIClient, APIError, IncorrectResponseError
import logging

logger = logging.getLogger(__name__)


class InvalidAccessTokenError(APIError):
    pass


class AccessTokenExpiredError(APIError):
    pass


class PermissionDeniedError(APIError):
    pass


ERROR_CODE_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_CODE_ACCESS_TOKEN_EXPIRED = 'access_token_expired'
ERROR_CODE_PERMISSION_DENIED = 'permission_denied'


class ResourceAPIClient(BaseAPIClient):
    API_VERSION = 'v1'

    def __init__(self, resource_api_base_url: str):
        self._resource_base_url = resource_api_base_url

    def get_current_time(self, access_token: str) -> str:
        url = self._build_full_url(endpoint='current_time')
        resp = requests.get(url, header=self._build_bearer_header(access_token))

        # Further improvement: pass jsonschema to the base method,
        # to have automated data validation.
        # Now we have only one field so we can check it manually.
        response_json = self.process_response(resp)
        current_time = response_json.get('current_time')
        if not access_token:
            logger.warning(
                "HTTP json body doesn't contain current_time field",
                extra={'url': resp.url, 'status_code': resp.status_code,
                       'json_body': response_json}
            )
            raise IncorrectResponseError("current_time field is missing")
        return current_time

    def get_epoch_time(self, access_token: str) -> str:
        url = self._build_full_url(endpoint='epoch_time')
        resp = requests.get(url, header=self._build_bearer_header(access_token))

        # Further improvement: pass jsonschema to the base method,
        # to have automated data validation.
        # Now we have only one field so we can check it manually.
        response_json = self.process_response(resp)
        epoch_time = response_json.get('epoch_time')
        if not access_token:
            logger.warning(
                "HTTP json body doesn't contain epoch_time field",
                extra={'url': resp.url, 'status_code': resp.status_code,
                       'json_body': response_json}
            )
            raise IncorrectResponseError("epoch_time field is missing")
        return epoch_time

    def raise_error_if_necessary(self, response: requests.Response,
                                 response_json: Optional[dict]) -> None:
        if not response_json:
            return
        error_code = response_json.get('error')
        error_description = response_json.get('error_description')
        if error_code == ERROR_CODE_INVALID_ACCESS_TOKEN:
            raise InvalidAccessTokenError(error_description)
        if error_code == ERROR_CODE_ACCESS_TOKEN_EXPIRED:
            raise AccessTokenExpiredError(error_description)
        if error_code == ERROR_CODE_PERMISSION_DENIED:
            raise PermissionDeniedError(error_description)

    def _build_full_url(self, endpoint: str) -> str:
        return f'{self._resource_base_url}/{self.API_VERSION}/{endpoint}'

    @staticmethod
    def _build_bearer_header(access_token: str) -> dict:
        return {'Authorization': f'Bearer {access_token}'}