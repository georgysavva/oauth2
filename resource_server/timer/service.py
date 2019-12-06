from apis.auth import AuthAPI
from models import models
from datetime import datetime
from typing import List
from timer.exceptions import PermissionDeniedError
import logging

logger = logging.getLogger(__name__)


class TimerService:
    def __init__(self, auth_api: AuthAPI):
        self._auth_api = auth_api

    def get_current_time(self, access_token: str) -> datetime:
        # Further improvement:
        # create something like a service middleware, that will check and obtain token info,
        # and pass validated data to the actual functions with business logic.
        token_info = self._get_token_info(access_token)
        self._check_scope(token_info.scope, 'current_time')
        return datetime.utcnow()

    def get_epoch_time(self, access_token: str) -> int:
        # Further improvement:
        # create something like a service middleware, that will check and obtain token info,
        # and pass validated data to the actual functions with business logic.
        token_info = self._get_token_info(access_token)
        self._check_scope(token_info.scope, 'epoch_time')
        return int(datetime.utcnow().timestamp())

    def _get_token_info(self, access_token: str) -> models.AccessTokenInfo:
        return self._auth_api.get_access_token_info(access_token)

    @staticmethod
    def _check_scope(scope: List[str], resource: str) -> None:
        if resource not in scope:
            logger.warning("Resource not in the token scope",
                        extra={'scope': scope, 'resource': resource})
            raise PermissionDeniedError(
                f"Access to resource {resource} denied, out of the token scope",
                resource
            )
