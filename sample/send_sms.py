""" Sample code to access SMS """

import os
from cudy_router import CudyRouter
from cudy_router.sms_manager import get_sms_manager

CUDY_HOST = os.environ['CUDY_HOST']
CUDY_USERNAME = os.environ['CUDY_USERNAME']
CUDY_PASSWORD = os.environ['CUDY_PASSWORD']
CUDY_PORT = os.environ['CUDY_PORT']

SMS_RECIPIENT = os.environ['SMS_RECIPIENT']

router = CudyRouter(CUDY_HOST, CUDY_USERNAME, CUDY_PASSWORD, CUDY_PORT)

if not router.authenticate():
    print("Authentication error")
    exit()

sms_manager = get_sms_manager(router)

response = sms_manager.send_sms(SMS_RECIPIENT, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

with open("response_send_sms.html", "w", encoding='utf-8') as fresponse:
    fresponse.write(response)
