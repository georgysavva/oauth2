import logging
from datetime import datetime
from typing import List

import jwt

from models import models
from oauth2 import exceptions

logger = logging.getLogger(__name__)


class AccessTokenManager:
    JWT_ALGORITHM = 'HS256'

    def __init__(
        self,
        applications_repo: models.ApplicationsRepository,
        default_users_scope: List[str], issuer_url: str, jwt_secret: str,
        token_lifetime: int
    ):
        self._apps_repo = applications_repo
        self._users_scope = default_users_scope
        self._jwt_secret = jwt_secret
        self._issuer_endpoint = issuer_url
        self._token_lifetime = token_lifetime  # in seconds

    def issue_token(self, grant_type: str, client_id: str, client_secret: str,
                    username: str) -> str:
        if grant_type != models.GRANT_TYPE_PASSWORD:
            logger.warning(
                "Token request has unsupported grant type", extra={'grant_type': grant_type}
            )
            raise exceptions.UnsupportedGrantTypeError(
                f"Unsupported grant type. "
                f"Server only supports f{models.GRANT_TYPE_PASSWORD} grant type."
            )
        application = self._apps_repo.get(client_id)
        if not application or application.client_secret != client_secret:
            log_ctx = {'client_id': client_id}
            if not application:
                logger.info("Application with that client id not found", extra=log_ctx)
            if application.client_secret != client_secret:
                logger.info("Client secrets don't match", extra=log_ctx)
            raise exceptions.InvalidClientError(
                f"Client with id {client_id} not found "
                f"or pair client_id and client_secret does not match"
            )
        # Now we should check username and password and found the corresponding user in the db
        # But since we grant access token to anyone we won't do that
        user_id = username

        scope = " ".join(self._users_scope)
        access_token = self._create_token(user_id, client_id, scope)
        return access_token

    def get_token_info(self, token: str) -> models.AccessTokenInfo:
        token_info = self._decode_jwt_token(token)
        # We don't need to check expires_at and issued_at here,
        # because it was check by the JWT implementation.
        # So can just return the token info
        return token_info

    def _create_token(self, user_id: str, client_id: str, scope: str) -> str:
        issued_at = int(datetime.utcnow().timestamp())
        expires_at = issued_at + self._token_lifetime
        token_info = models.AccessTokenInfo(user_id, client_id, issued_at, expires_at, scope)
        token = self._encode_jwt_token(token_info)
        return token

    def _encode_jwt_token(self, token_info: models.AccessTokenInfo) -> str:
        payload = {
            'sub': token_info.user_id,
            'iss': self._issuer_endpoint,
            'cid': token_info.client_id,
            'iat': token_info.issued_at,
            'exp': token_info.expires_at,
            'scope': token_info.scope,
        }
        return jwt.encode(payload, self._jwt_secret, self.JWT_ALGORITHM)

    def _decode_jwt_token(self, token: str) -> models.AccessTokenInfo:
        try:
            payload = jwt.decode(token, self._jwt_secret, algorithms=[self.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError as e:
            logger.info("JWT token expired: %s", e)
            raise exceptions.AccessTokenExpiredError("Access token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning("JWT token validation failed", extra={'error': e})
            raise exceptions.InvalidAccessTokenError
        # Validate presence and type of field that are not validates by the jwt library.
        for field in ['sub', 'cid', 'scope']:
            value = payload.get(field)
            if type(value) != str:
                logger.warning("JWT payload doesn't contain all required fields with proper types",
                               extra={'payload': payload})
                raise exceptions.InvalidAccessTokenError
        return models.AccessTokenInfo(
            user_id=payload['sub'],
            client_id=payload['cid'],
            issued_at=payload['iat'],
            expires_at=payload['exp'],
            scope=payload['scope'],
        )
