import logging
from typing import Generator

from plugin.connector.base import JiraBaseConnector

_LOGGER = logging.getLogger("spaceone")


class ServerInfoConnector(JiraBaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_jira_instance_info(self, secret_data: dict) -> dict:
        response = self.dispatch_request("GET", "rest/api/3/serverInfo", secret_data)

        return next(response)
