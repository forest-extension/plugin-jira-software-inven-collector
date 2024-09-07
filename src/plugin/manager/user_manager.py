import logging
from typing import Generator

from plugin.connector.project_connector import ProjectConnector
from plugin.connector.user_connector import UserConnector
from plugin.manager.base import JiraBaseManager
from spaceone.inventory.plugin.collector.lib import *

_LOGGER = logging.getLogger("spaceone")


class MemberManager(JiraBaseManager):
    cloud_service_group = "Projects"
    cloud_service_type = "Member"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Projects"
        self.cloud_service_type = "Member"
        self.metadata_path = "metadata/projects/user.yaml"
        self.project_connector = ProjectConnector()
        self.role_connector = UserConnector()

    def collect(
        self, options: dict, secret_data: dict, schema: str
    ) -> Generator[dict, None, None]:
        try:
            yield from self.collect_cloud_service_type(options, secret_data, schema)
            yield from self.collect_cloud_service(options, secret_data, schema)

        except Exception as e:
            _LOGGER.error(f"[collect] Error {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
            )

    def collect_cloud_service_type(self, options, secret_data, schema):
        tags = {
            "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/jira-icon.png"
        }

        cloud_service_type = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=False,
            tags=tags,
            labels=["Management"],
        )

        yield make_response(
            cloud_service_type=cloud_service_type,
            match_keys=[["name", "group", "provider"]],
            resource_type="inventory.CloudServiceType",
        )

    def collect_cloud_service(self, options, secret_data, schema):
        # Return Cloud Service
        domain = secret_data["domain"]
        project_key = secret_data.get("project_key")

        for user_info in self.role_connector.get_all_project_roles(
            secret_data, project_key
        ):
            reference = {
                "resource_id": f"jira:{user_info['accountId']}",
                "external_link": f"https://{domain}.atlassian.net/browse/{user_info['accountId']}",
            }

            cloud_service = make_cloud_service(
                name=user_info["displayName"],
                cloud_service_type=self.cloud_service_type,
                cloud_service_group=self.cloud_service_group,
                provider=self.provider,
                data=user_info,
                reference=reference,
                account=domain,
            )

            yield make_response(
                cloud_service=cloud_service,
                match_keys=[
                    [
                        "reference.resource_id",
                        "provider",
                        "cloud_service_type",
                        "cloud_service_group",
                        "account",
                    ]
                ],
            )
