from models import models
from typing import Dict, Optional


# In the real world service we would use a database to store applications e.g: PostgreSQL, MongoDB.
# And we should encrypt "client_secret" field to improve security of the system.
# But for now we will go with the simplest implementation.
class InMemApplicationsRepo(models.ApplicationsRepository):
    def __init__(self):
        self._applications: Dict[str, models.Application] = {}

    def create_if_not_exists(self, application: models.Application) -> models.Application:
        if application.client_id not in self._applications:
            self._applications[application.client_id] = application
        return application

    def get(self, client_id: str) -> Optional[models.Application]:
        return self._applications.get(client_id)
