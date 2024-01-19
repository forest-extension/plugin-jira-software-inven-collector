import logging

from spaceone.core.service import *
from spaceone.core.error import ERROR_REQUIRED_PARAMETER
from spaceone.inventory.plugin.collector.lib.server import CollectorPluginServer
from plugin.connector.server_info_connector import ServerInfoConnector

from plugin.manager.base import JiraBaseManager

_LOGGER = logging.getLogger("spaceone")

app = CollectorPluginServer()


@app.route("Collector.init")
def collector_init(params: dict) -> dict:
    """init plugin by options

    Args:
        params (CollectorInitRequest): {
            'options': 'dict',    # Required
            'domain_id': 'str'
        }

    Returns:
        PluginResponse: {
            'metadata': 'dict'
        }
    """

    return {"metadata": {}}


@app.route("Collector.verify")
def collector_verify(params: dict) -> None:
    """Verifying collector plugin

    Args:
        params (CollectorVerifyRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'domain_id': 'str'
        }

    Returns:
        None
    """
    pass


@app.route("Collector.collect")
def collector_collect(params: dict) -> dict:
    """Collect external data

    Args:
        params (CollectorCollectRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'task_options': 'dict',
            'domain_id': 'str'
        }

    Returns:
        Generator[ResourceResponse, None, None]
        {
            'state': 'SUCCESS | FAILURE',
            'resource_type': 'inventory.CloudService | inventory.CloudServiceType | inventory.Region',
            'cloud_service_type': CloudServiceType,
            'cloud_service': CloudService,
            'region': Region,
            'match_keys': 'list',
            'error_message': 'str'
            'metadata': 'dict'
        }

        CloudServiceType
        {
            'name': 'str',           # Required
            'group': 'str',          # Required
            'provider': 'str',       # Required
            'is_primary': 'bool',
            'is_major': 'bool',
            'metadata': 'dict',      # Required
            'service_code': 'str',
            'tags': 'dict'
            'labels': 'list'
        }

        CloudService
        {
            'name': 'str',
            'cloud_service_type': 'str',  # Required
            'cloud_service_group': 'str', # Required
            'provider': 'str',            # Required
            'ip_addresses' : 'list',
            'account' : 'str',
            'instance_type': 'str',
            'instance_size': 'float',
            'region_code': 'str',
            'data': 'dict'               # Required
            'metadata': 'dict'           # Required
            'reference': 'dict'
            'tags' : 'dict'
        }

        Region
        {
            'name': 'str',
            'region_code': 'str',        # Required
            'provider': 'str',           # Required
            'tags': 'dict'
        }

        Only one of the cloud_service_type, cloud_service and region fields is required.
    """

    secret_data = params["secret_data"]
    options = params["options"]

    check_secret_data(secret_data)

    for cloud_service_manager in JiraBaseManager.get_all_managers(options):
        cloud_svc_mgr = cloud_service_manager()
        yield from cloud_svc_mgr.collect(
            options=options, secret_data=secret_data, schema=""
        )


@app.route("Job.get_tasks")
def job_get_tasks(params: dict) -> dict:
    """Get job tasks

    Args:
        params (JobGetTaskRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'domain_id': 'str'
        }

    Returns:
        TasksResponse: {
            'tasks': 'list'
        }

    """
    pass


def check_secret_data(secret_data: dict):
    if secret_data.get("domain") is None:
        raise ERROR_REQUIRED_PARAMETER(key="secret_data.domain")

    if secret_data.get("user_id") is None:
        raise ERROR_REQUIRED_PARAMETER(key="secret_data.user_id")

    if secret_data.get("api_token") is None:
        raise ERROR_REQUIRED_PARAMETER(key="secret_data.api_token")
