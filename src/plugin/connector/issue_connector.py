import logging
from typing import Generator

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
    ) -> dict:
        params = {
            "jql": f"project = '{project_id_or_key}' AND created >= startOfYear(-1) order by created DESC",
            "startAt": 0,
            "maxResults": 500,
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
            ],
        }
        request_url = "rest/api/3/search"
        _LOGGER.debug(f"[search_issue] {request_url}")

        responses = self.dispatch_request(
            "GET", request_url, secret_data, params=params
        )

        return next(responses)
