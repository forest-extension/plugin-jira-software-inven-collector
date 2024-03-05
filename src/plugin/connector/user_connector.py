import logging
from typing import Generator

from plugin.connector.base import JiraBaseConnector

_LOGGER = logging.getLogger("spaceone")


class UserConnector(JiraBaseConnector):
    cloud_service_type = "User"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_all_project_roles(
        self,
        secret_data: dict,
        project_id_or_key: str,
    ) -> list:
        request_url = f"rest/api/3/user/assignable/multiProjectSearch"
        _LOGGER.debug(f"[search_role] {request_url}")

        query = {"projectKeys": project_id_or_key}

        responses = self.dispatch_request("GET", request_url, secret_data, params=query)

        return responses
