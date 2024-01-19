import logging

from typing import Generator

from plugin.connector.server_info_connector import ServerInfoConnector
from plugin.manager.base import JiraBaseManager
from spaceone.inventory.plugin.collector.lib import *

_LOGGER = logging.getLogger("spaceone")


class ServerInfoManager(JiraBaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_info_connector = ServerInfoConnector()

    def collect(
        self, options: dict, secret_data: dict, schema: str
    ) -> Generator[dict, None, None]:
        try:
            yield from self.collect_region(options, secret_data, schema)

        except Exception as e:
            _LOGGER.error(f"[collect] Error {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group="Region",
                cloud_service_type="Region",
            )

    def collect_region(self, options, secret_data, schema):
        server_info = self.server_info_connector.get_jira_instance_info(secret_data)
        locale = server_info.get("defaultLocale").get("locale", "Global")
        yield {
            "name": locale,
            "region_code": "Global",
            "provider": self.provider,
            "tags": {},
        }
