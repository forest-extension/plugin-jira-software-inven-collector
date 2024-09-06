import logging
from typing import Generator

import requests

from plugin.connector.base import JiraBaseConnector

_LOGGER = logging.getLogger("spaceone")


class IssueConnector(JiraBaseConnector):
    cloud_service_type = "Issue"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def search_issue(
        self,
        secret_data: dict,
        project_id_or_key: str,
    ) -> list:
        request_url = "rest/api/3/search"
        _LOGGER.debug(f"[search_issue] {request_url}")

        start_at = 0
        max_results = 100
        while True:
            # Set up request
            url = f"{self.get_base_url(secret_data)}{request_url}"
            headers = {"Accept": "application/json"}
            auth = self.get_auth(secret_data)

            params = {
                "jql": f"project = '{project_id_or_key}' AND created >= startOfYear(-1) order by created DESC",
                "startAt": start_at,
                "maxResults": max_results,
                "fields": [
                    "summary",
                    "comment",
                    "created",
                    "creator",
                    "assignee",
                    "duedate",
                    "issuelinks",
                    "issuetype",
                    "labels",
                    "lastViewed",
                    "priority",
                    "progress",
                    "project",
                    "reporter",
                    "resolution",
                    "resolutiondate",
                    "status",
                    "statuscategorychangedate",
                    "subtasks",
                    "updated",
                    "watches",
                    "-avatarUrls",
                ],
            }

            response = requests.request(
                "GET", url, headers=headers, params=params, auth=auth
            )

            if response.status_code != 200:
                _LOGGER.error(
                    f"Failed to fetch issues: {response.status_code} {response.text}"
                )
                break

            response_json = response.json()
            issues = response_json.get("issues", [])
            for issue in issues:
                yield issue

            total = response_json.get("total", 0)
            start_at += max_results

            if start_at >= total:
                break
