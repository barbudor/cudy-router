"""Modem Manager"""

from typing import List, Union

from . import CudyRouter
from . import cudy_parser
from .models.device import DevicesInfo


class DevicesManager:
    def __init__(self, cudy_router):
        """Initialize."""
        self.cudy_router = cudy_router

    def  get_devices(self, devices_list: Union[str, List[str]] = "*") -> DevicesInfo:
        """Retrieves devices infos from the router"""

        devices_info = cudy_parser.get_devices_info(
            self.cudy_router.get("admin/network/devices/devlist?detail=1"),
            devices_list,
        )

        return DevicesInfo.model_validate(devices_info)


def get_devices_manager(cudy_router: CudyRouter) -> DevicesManager:
    return DevicesManager(cudy_router)
