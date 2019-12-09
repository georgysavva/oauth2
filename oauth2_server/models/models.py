from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import List

GRANT_TYPE_AUTHORIZATION_CODE = 'code'
GRANT_TYPE_PASSWORD = 'password'
GRANT_TYPE_CLIENT_CREDENTIALS = 'client_credentials'
GRANT_TYPE_IMPLICIT = 'implicit'
GRANT_TYPES = [GRANT_TYPE_AUTHORIZATION_CODE, GRANT_TYPE_PASSWORD, GRANT_TYPE_CLIENT_CREDENTIALS,
               GRANT_TYPE_IMPLICIT]


@dataclass
class Application:
    client_id: str
    client_secret: str


# For now we don't have any persistence for users, since we grant access tokens to every one.
@dataclass
class User:
    id: str
    username: str
    full_name: str


# We use JWT to sign and verify access tokens, therefore we don't need to store them anywhere,
# because JWT is a self encoded type of tokens.
@dataclass
class AccessTokenInfo:
    user_id: str
    client_id: str
    issuer_url: str
    issued_at: int
    expires_at: int
    scope: List[str]


class ApplicationsRepository(metaclass=abc.ABCMeta):
    """
    This is an interface for Applications storage. It can be implemented in memory or in a DB.
    """
    @abc.abstractmethod
    def get(self, client_id: str) -> Application:
        pass

    @abc.abstractmethod
    def create_if_not_exists(self, application: Application) -> Application:
        pass

    def create_default_apps(self, apps_data: List[dict]) -> ApplicationsRepository:
        applications = [
            Application(client_id=data['client_id'], client_secret=data['client_secret'])
            for data in apps_data
        ]
        for app in applications:
            self.create_if_not_exists(app)
        return self
