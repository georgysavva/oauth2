from __future__ import annotations
from dataclasses import dataclass
from typing import List
import abc

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


@dataclass
class User:
    id: str
    full_name: str


class ApplicationsRepository(metaclass=abc.ABCMeta):
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
