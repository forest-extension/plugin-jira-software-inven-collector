import logging

from typing import Generator

from plugin.connector.project_connector import ProjectConnector
from plugin.manager.base import JiraBaseManager
from spaceone.inventory.plugin.collector.lib import *

_LOGGER = logging.getLogger("spaceone")


class ProjectManager(JiraBaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Projects"
        self.cloud_service_type = "Project"
        self.metadata_path = "metadata/projects/project.yaml"
        self.project_connector = ProjectConnector()

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
            is_major=True,
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
        project_info = self.project_connector.get_project(secret_data, project_key)

        total = self.project_connector.get_project_total_issue_count(
            secret_data, project_key
        )

        project_info.update(
            {
                "display_total_issue_count": total,
                "display_issue_type_count": len(project_info.get("issueTypes", [])),
            }
        )

        reference = {
            "resource_id": f"jira:{project_info['id']}",
            "external_link": f"https://{domain}.atlassian.net/browse/{project_info['key']}",
        }

        cloud_service = make_cloud_service(
            name=project_info["name"],
            cloud_service_type=self.cloud_service_type,
            cloud_service_group=self.cloud_service_group,
            provider=self.provider,
            data=project_info,
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
