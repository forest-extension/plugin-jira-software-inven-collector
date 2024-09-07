import logging
import os
from typing import Generator

from spaceone.core.error import *
from spaceone.core.manager import BaseManager
from spaceone.core import utils
from spaceone.inventory.plugin.collector.lib import *

_LOGGER = logging.getLogger("spaceone")

_CURRENT_DIR = os.path.dirname(__file__)
_METRIC_DIR = os.path.join(_CURRENT_DIR, "../metrics/")
_METADATA_DIR = os.path.join(_CURRENT_DIR, "../metadata/")


class JiraBaseManager(BaseManager):
    provider = "jira"
    cloud_service_group = None
    cloud_service_type = None
    region_name = None
    metadata_path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def collect(
        self, options: dict, secret_data: dict, schema: str
    ) -> Generator[dict, None, None]:
        raise NotImplementedError("Method not implemented!")

    @classmethod
    def get_all_managers(cls, options):
        cloud_service_types_option = options.get("cloud_service_types")
        if cloud_service_types_option:
            subclasses = []
            for subclass in cls.__subclasses__():
                if (
                    subclass.__name__.replace("Manager", "")
                    in cloud_service_types_option
                ):
                    subclasses.append(subclass)
            return subclasses

        else:
            return cls.__subclasses__()

    @classmethod
    def get_all_cloud_service_group(cls) -> list:
        cloud_service_groups = []
        for subclass in cls.__subclasses__():
            cloud_service_groups.append(subclass.cloud_service_group)
        return list(set(cloud_service_groups))

    @classmethod
    def collect_metrics(cls, cloud_service_group: str):
        if not os.path.exists(os.path.join(_METRIC_DIR, cloud_service_group)):
            os.mkdir(os.path.join(_METRIC_DIR, cloud_service_group))
        for dirname in os.listdir(os.path.join(_METRIC_DIR, cloud_service_group)):
            for filename in os.listdir(
                os.path.join(_METRIC_DIR, cloud_service_group, dirname)
            ):
                if filename.endswith(".yaml"):
                    file_path = os.path.join(
                        _METRIC_DIR, cloud_service_group, dirname, filename
                    )
                    info = utils.load_yaml_from_file(file_path)
                    if filename == "namespace.yaml":
                        yield make_response(
                            namespace=info,
                            resource_type="inventory.Namespace",
                            match_keys=[],
                        )
                    else:
                        yield make_response(
                            metric=info, resource_type="inventory.Metric", match_keys=[]
                        )

    def error_response(
        self, error: Exception, resource_type: str = "inventory.CloudService"
    ) -> dict:
        if not isinstance(error, ERROR_BASE):
            error = ERROR_UNKNOWN(message=error)

        _LOGGER.error(
            f"[error_response] ({self.region_name}) {error.error_code}: {error.message}",
            exc_info=True,
        )
        return {
            "state": "FAILURE",
            "message": error.message,
            "resource_type": "inventory.ErrorResource",
            "resource": {
                "provider": self.provider,
                "cloud_service_group": self.cloud_service_group,
                "cloud_service_type": self.cloud_service_type,
                "resource_type": resource_type,
            },
        }
