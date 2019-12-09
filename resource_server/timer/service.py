import logging
from datetime import datetime, timezone
from typing import List

from apis.auth import AuthAPI, AuthorizationError
from models import models
from timer.exceptions import PermissionDeniedError

logger = logging.getLogger(__name__)


class TimerService:
    """
    This class contains resource business logic layer.
    It requests access token information from the oauth2 server and validates
    that the token scope includes requested resource.
    If request is valid it return the resource (current_time or epoch_time).
    """

    def __init__(self, auth_api: AuthAPI):
        self._auth_api = auth_api

    def get_current_time(self, access_token: str) -> datetime:
        # Further improvement:
        # create something like a service middleware, that will check and obtain token info,
        # and pass validated data to the actual functions with business logic.
        logger.info("Get current time request received")
        token_info = self._get_token_info(access_token)
        self._check_scope(token_info.scope, 'current_time')
        result = self._get_utc_now()
        logger.info("Return current time resource", extra={'current_time': result})
        return result

    def get_epoch_time(self, access_token: str) -> int:
        # Further improvement:
        # create something like a service middleware, that will check and obtain token info,
        # and pass validated data to the actual functions with business logic.
        logger.info("Get epoch time request received")
        token_info = self._get_token_info(access_token)
        self._check_scope(token_info.scope, 'epoch_time')
        result = int(self._get_utc_now().timestamp())
        logger.info("Return epoch time resource", extra={'epoch_time': result})
        return result

    def _get_token_info(self, access_token: str) -> models.AccessTokenInfo:
        logger.info("Verify and get access token info from oauth2 server")
        try:
            return self._auth_api.get_access_token_info(access_token)
        except AuthorizationError as e:
            logger.warning("Access token authorization failed", extra={'error': e})
            raise

    @staticmethod
    def _check_scope(scope: List[str], resource: str) -> None:
        if resource not in scope:
            logger.warning(
                "Resource not in the token scope", extra={'scope': scope, 'resource': resource}
            )
            raise PermissionDeniedError(
                f"Access to resource {resource} denied, out of the token scope"
            )

    @staticmethod
    def _get_utc_now() -> datetime:
        return datetime.now(timezone.utc)
