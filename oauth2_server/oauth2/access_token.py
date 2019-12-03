from models import models
from oauth2 import exceptions
import logging

logger = logging.getLogger(__name__)


class AccessTokenManager:
    def __init__(self, applications_repo: models.ApplicationsRepository):
        self.apps_repo = applications_repo

    def issue_token(self, grant_type: str, client_id: str, client_secret: str, username: str,
                    password: str):
        if grant_type != models.GRANT_TYPE_PASSWORD:
            logger.warning(f"Token request has unsupported grant type: {grant_type}")
            # raise exceptions.UnsupportedGrantTypeError(
            #     f"Unsupported grant type. "
            #     f"Server only supports f{models.GRANT_TYPE_PASSWORD} grant type."
            # )
        # application = self.apps_repo.get(client_id)
        # if not application or application.client_secret != client_secret:
        #     if not application:
        #         logger.info("Application with client")
