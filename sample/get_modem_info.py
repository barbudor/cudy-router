""" Sample code using modem_info """

import os
from cudy_router import CudyRouter
from cudy_router.modem_manager import get_modem_manager

CUDY_HOST = os.environ['CUDY_HOST']
CUDY_USERNAME = os.environ['CUDY_USERNAME']
CUDY_PASSWORD = os.environ['CUDY_PASSWORD']
CUDY_PORT = os.environ['CUDY_PORT']

router = CudyRouter(CUDY_HOST, CUDY_USERNAME, CUDY_PASSWORD, CUDY_PORT)

if not router.authenticate():
    print("Authentication error")
    exit()

modem_manager = get_modem_manager(router)

modem_info = modem_manager.get_modem_info()
print(modem_info.model_dump_json(indent=2))
