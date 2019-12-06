import json
import logging
import os
import sys
from typing import Optional, List

import requests

from apis.exceptions import IncorrectResponseError, InvalidRequestError
import jsonschema

logger = logging.getLogger(__name__)

ERROR_CODE_INVALID_REQUEST = 'invalid_request'


# Further improvement: move this class to a library,
# because it used in both resource_server and webapp services.
class BaseAPIClient:
    api_version = 'v1'
    json_schemas_dir = 'json_schemas'
    schema_names: Optional[List[str]] = None

    def __init__(self, api_base_url: str):
        self._api_base_url = api_base_url
        if self.json_schemas_dir and self.schema_names:
            abs_schemas_dir_path = self._build_abs_path_to_schemas_dir()
            self._json_schemas = self._load_schemas(abs_schemas_dir_path)
        else:
            self._json_schemas = None

    def _build_abs_path_to_schemas_dir(self) -> str:
        # BaseAPIClient doesn't know the location of the actual (children) classes
        # It needs to get the real children module instead of its own.
        actual_module = sys.modules[self.__class__.__module__]
        actual_module_path = os.path.abspath(actual_module.__file__)
        actual_package_path = os.path.dirname(actual_module_path)
        abs_path_to_schemas_dir = os.path.abspath(
            os.path.join(actual_package_path, self.json_schemas_dir)
        )
        return abs_path_to_schemas_dir

    def _load_schemas(self, abs_schemas_dir_path: str):
        if not self.schema_names:
            return
        loaded_schemas = {}
        for schema_name in self.schema_names:
            schema_path = os.path.join(abs_schemas_dir_path, schema_name + '.json')
            try:
                with open(schema_path) as f:
                    schema_data = json.load(f)
            except Exception as e:
                raise RuntimeError(f"Can't load json schema from file {schema_path}: {e}") from e
            loaded_schemas[schema_name] = schema_data
        return loaded_schemas

    def _process_response(self, response: requests.Response, schema_name=None,
                          json_body_required=True) -> Optional[dict]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None
        self._raise_error_if_necessary(response, response_json)
        response.raise_for_status()
        if (json_body_required or schema_name) and not response_json:
            raise IncorrectResponseError("Empty json body", response)
        if schema_name:
            validation_schema = self._json_schemas[schema_name]
            try:
                jsonschema.validate(response_json, validation_schema)
            except jsonschema.ValidationError as e:
                logger.warning(
                    "HTTP response failed json schema validation",
                    extra={
                        'url': response.url, 'status_code': response.status_code,
                        'response_body': response_json, 'json_schema': schema_name,
                        'error': e.message
                    }
                )
                raise IncorrectResponseError(f"Response body validation failed: {e.message}",
                                             response) from e
                pass
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
