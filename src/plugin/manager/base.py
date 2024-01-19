import logging
from typing import Generator

from spaceone.core.error import *
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger("spaceone")


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
