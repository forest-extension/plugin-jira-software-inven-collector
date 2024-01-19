import logging
from typing import Generator

from plugin.connector.project_connector import ProjectConnector
from plugin.connector.issue_connector import IssueConnector
from plugin.manager.base import JiraBaseManager
from spaceone.inventory.plugin.collector.lib import *

_LOGGER = logging.getLogger("spaceone")


class IssueManager(JiraBaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Projects"
        self.cloud_service_type = "Issue"
        self.metadata_path = "metadata/projects/issue.yaml"
        self.project_connector = ProjectConnector()
        self.issue_connector = IssueConnector()

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
        )

        yield make_response(
            cloud_service_type=cloud_service_type,
            match_keys=[["name", "group", "provider"]],
            resource_type="inventory.CloudServiceType",
        )

    def collect_cloud_service(self, options, secret_data, schema):
        # Return Cloud Service
        domain = secret_data["domain"]
        for project_info in self.project_connector.get_projects(secret_data):
            project_id_or_key = project_info["id"]
            for issue_info in self.issue_connector.search_issue(
                secret_data, project_id_or_key
            ).get("issues", []):
                reference = {
                    "resource_id": f"jira:{issue_info['id']}",
                    "external_link": f"https://{domain}.atlassian.net/browse/{issue_info['key']}",
                }

                cloud_service = make_cloud_service(
                    name=issue_info["fields"]["summary"],
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=issue_info,
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
