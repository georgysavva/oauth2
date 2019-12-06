import logging
from typing import Optional

import requests

from apis.exceptions import IncorrectResponseError, InvalidRequestError

logger = logging.getLogger(__name__)

ERROR_CODE_INVALID_REQUEST = 'invalid_request'


class BaseAPIClient:
    def process_response(self, response: requests.Response, json_body_required=True
                         ) -> Optional[dict]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None
        self.raise_error_if_necessary(response, response_json)
        response.raise_for_status()
        if json_body_required and not response_json:
            logger.warning(
                "HTTP response has empty json body",
                extra={'url': response.url, 'status_code': response.status_code,
                       'body': response.text}
            )
            raise IncorrectResponseError("Empty json body")
        return response_json

    def raise_error_if_necessary(self, response: requests.Response,
                                 response_json: Optional[dict]) -> None:
        if not response_json:
            return
        error_code = response_json.get('error')
        error_description = response_json.get('error_description')
        if error_code == ERROR_CODE_INVALID_REQUEST:
            logger.warning(
                "HTTP bad request",
                extra={'url': response.url, 'status_code': response.status_code,
                       'json_body': response_json}
            )
            raise InvalidRequestError(error_description)
