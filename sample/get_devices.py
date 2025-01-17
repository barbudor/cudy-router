""" Sample code using devices """

import os
from cudy_router import CudyRouter
from cudy_router.devices_manager import get_devices_manager

CUDY_HOST = os.environ['CUDY_HOST']
CUDY_USERNAME = os.environ['CUDY_USERNAME']
CUDY_PASSWORD = os.environ['CUDY_PASSWORD']
CUDY_PORT = os.environ['CUDY_PORT']

router = CudyRouter(CUDY_HOST, CUDY_USERNAME, CUDY_PASSWORD, CUDY_PORT)

if not router.authenticate():
    print("Authentication error")
    exit()

devices_manager = get_devices_manager(router)

devices_info = devices_manager.get_devices()
print(devices_info.model_dump_json(indent=2))
