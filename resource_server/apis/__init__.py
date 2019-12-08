import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

ERROR_CODE_INVALID_REQUEST = 'invalid_request'


# Further improvement: move this class to a library,
# because it used in both resource_server and webapp services.
class BaseAPIClient:
    api_version = 'v1'

    def __init__(self, api_base_url: str):
        self._api_base_url = api_base_url

    def _process_response(self, response: requests.Response, json_body_required: bool = True
                          ) -> dict:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None
        self._raise_error_if_necessary(response, response_json)
        response.raise_for_status()
        return self._validate_response(response, response_json, json_body_required)

    @staticmethod
    def _validate_response(response: requests.Response, response_json: dict,
                           json_body_required: bool = True) -> dict:
        if json_body_required and not response_json:
            logger.warning(
                "HTTP response has empty json body",
                extra={'url': response.url, 'status_code': response.status_code,
                       'response_body': response.text}
            )
            raise IncorrectResponseError("Empty json body", response)

        return response_json

    def _raise_error_if_necessary(self, response: requests.Response,
                                  response_json: Optional[dict]) -> None:
        if not response_json:
            return
        error_code = response_json.get('error')
        error_description = response_json.get('error_description')
        if error_code == ERROR_CODE_INVALID_REQUEST:
            logger.warning(
                "HTTP response contain invalid_request error code",
                extra={'url': response.url, 'status_code': response.status_code,
                       'response_body': response_json, 'request_body': response.request.json}
            )
            raise InvalidRequestError(error_description, response)

    def _build_full_url(self, endpoint: str) -> str:
        return f'{self._api_base_url}/{self.api_version}/{endpoint}'


class APIError(Exception):
    def __init__(self, message, response, *args):
        self.response = response
        super().__init__(message, *args)


class InvalidRequestError(APIError):
    pass


class IncorrectResponseError(APIError):
    pass
