import logging

import requests

from apis import BaseAPIClient, IncorrectResponseError

logger = logging.getLogger(__name__)


class AuthAPI(BaseAPIClient):
    def __init__(self, auth_api_base_url: str, client_id: str, client_secret: str,
                 http_timeout: int):
        self._client_id = client_id
        self._client_secret = client_secret
        self._http_timeout = http_timeout  # in seconds
        super().__init__(auth_api_base_url)

    def request_access_token(self, grant_type: str, username: str, password: str) -> str:
        url = self._build_full_url(endpoint='token')
        resp = requests.post(url, json={
            'grant_type': grant_type, 'client_id': self._client_id,
            'client_secret': self._client_secret, 'username': username,
            'password': password
        }, timeout=self._http_timeout)
        # Further improvement: pass json schema to the base method,
        # to have automated data validation.
        # Now we have only one field so we can check it manually.
        response_json = self._process_response(resp)
        access_token = response_json.get('access_token')
        if not access_token or type(access_token) != str:
            logger.warning(
                "HTTP response body doesn't contain 'access_token' field or wrong type",
                extra={'url': resp.url, 'status_code': resp.status_code,
                       'response_body': response_json}
            )
            raise IncorrectResponseError("'access_token' field is missing or wrong type", resp)
        return access_token
