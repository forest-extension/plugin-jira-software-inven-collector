import logging

from plugin.connector.base import JiraBaseConnector

_LOGGER = logging.getLogger("spaceone")


class ProjectConnector(JiraBaseConnector):
    cloud_service_type = "Project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_projects(self, secret_data: dict) -> list:
        params = {
            "maxResults": 100,
        }

        return self.dispatch_request(
            "GET", "rest/api/3/project/search", secret_data, params=params
        )

    def get_project(self, secret_data: dict, project_id_or_key: str) -> dict:
        params = {
            "expand": ["description", "lead", "issueTypes", "insight"],
            "fields": ["-customfield"],
        }

        response = self.dispatch_request(
            "GET", f"rest/api/3/project/{project_id_or_key}", secret_data, params=params
        )
        return next(response)

    def get_project_total_issue_count(
        self, secret_data: dict, project_id_or_key: str
    ) -> int:
        params = {"jql": f"project = '{project_id_or_key}'", "fields": ["-all"]}

        responses = self.dispatch_request(
            "GET", "rest/api/3/search", secret_data, params=params
        )

        return next(responses).get("total", 0)
