import logging
import requests
from requests.auth import HTTPBasicAuth
from typing import Union, Generator

from spaceone.core.error import *
from spaceone.core.connector import BaseConnector

__all__ = ["JiraBaseConnector"]

_LOGGER = logging.getLogger("spaceone")


class JiraBaseConnector(BaseConnector):
    cloud_service_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dispatch_request(
        self,
        method: str,
        url: str,
        secret_data: dict,
        data: dict = None,
        params: dict = None,
    ) -> Union[Generator[dict, None, None], list]:
        # Set up request
        url = f"{self.get_base_url(secret_data)}{url}"
        headers = {"Accept": "application/json"}
        auth = self.get_auth(secret_data)

        try:
            for response in self._pagination(method, url, headers, auth, params, data):
                yield response

        except Exception as e:
            _LOGGER.error(f"[dispatch_request] Error {e}")
            raise ERROR_UNKNOWN(message=e)

    @staticmethod
    def _pagination(
        method: str,
        url: str,
        headers: dict,
        auth: HTTPBasicAuth,
        params: dict,
        data: dict = None,
    ) -> list:
        responses = []
        while True:
            response = requests.request(
                method,
                url,
                headers=headers,
                auth=auth,
                params=params,
                json=data,
            )
            response_json = response.json()
            response_values = response_json.get("values")
            _LOGGER.debug(
                f"[dispatch_request] {url} {response.status_code} {response.reason}, {response_json.get('total')}"
            )

            if response.status_code != 200:
                raise ERROR_UNKNOWN(
                    message=f"Error {response.status_code} {response.text}"
                )

            if response_values:
                responses.extend(response_values)
            else:
                responses.append(response_json)

            if response_json.get("isLast", True) or response_json.get("isLast") is None:
                break
            else:
                url = response_json.get("nextPage")
        return responses

    @staticmethod
    def get_base_url(secret_data: dict) -> str:
        domain = secret_data.get("domain")
        return f"https://{domain}.atlassian.net/"

    @staticmethod
    def get_auth(secret_data: dict) -> HTTPBasicAuth:
        user_id = secret_data.get("user_id")
        api_token = secret_data.get("api_token")
        return HTTPBasicAuth(username=user_id, password=api_token)

    @classmethod
    def get_connector_by_service(cls, service: str, secret_data: dict) -> BaseConnector:
        for sub_cls in cls.__subclasses__():
            if sub_cls.cloud_service_type == service:
                return sub_cls(secret_data)
