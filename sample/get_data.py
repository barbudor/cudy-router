from cudy_router import CudyRouter
import os

CUDY_HOST = os.environ['CUDY_HOST']
CUDY_USERNAME = os.environ['CUDY_USERNAME']
CUDY_PASSWORD = os.environ['CUDY_PASSWORD']

router = CudyRouter(CUDY_HOST, CUDY_USERNAME, CUDY_PASSWORD)

router.authenticate()

data = router.get_data(device_list="*")
print(repr(data))
