"""Modem Manager"""

from . import CudyRouter
from . import cudy_parser
from .models.modem import ModemInfo


class ModemManager:
    def __init__(self, cudy_router):
        """Initialize."""
        self.cudy_router = cudy_router

    def  get_modem_info(self) -> ModemInfo:
        """Retrieves Modem infos from the router"""

        modem_info = cudy_parser.get_modem_info(
            f"{self.cudy_router.get('admin/network/gcom/status')}{self.cudy_router.get('admin/network/gcom/status?detail=1')}"
        )
        return ModemInfo.model_validate(modem_info)


def get_modem_manager(cudy_router: CudyRouter) -> ModemManager:
    return ModemManager(cudy_router)

