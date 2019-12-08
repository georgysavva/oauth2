import logging
from typing import Optional

import requests

from apis import BaseAPIClient
from apis.exceptions import InvalidAccessTokenError, AccessTokenExpiredError
from models import models

logger = logging.getLogger(__name__)

ERROR_CODE_INVALID_ACCESS_TOKEN = 'invalid_access_token'
ERROR_CODE_ACCESS_TOKEN_EXPIRED = 'access_token_expired'


class AuthAPI(BaseAPIClient):
    schema_names = ['access_token_info_response']

    def __init__(self, auth_api_base_url: str):
        super().__init__(auth_api_base_url)

    def get_access_token_info(self, access_token: str) -> models.AccessTokenInfo:
        url = self._build_full_url(endpoint='token')
        resp = requests.post(url, json={'access_token': access_token})
        response_json = self._process_response(resp, schema_name='access_token_info_response')
        return models.AccessTokenInfo(response_json['user_id'], response_json['scope'])

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
