""" Sample code to access SMS """

import os
from cudy_router import CudyRouter
from cudy_router.sms_manager import get_sms_manager

CUDY_HOST = os.environ['CUDY_HOST']
CUDY_USERNAME = os.environ['CUDY_USERNAME']
CUDY_PASSWORD = os.environ['CUDY_PASSWORD']
CUDY_PORT = os.environ['CUDY_PORT']

router = CudyRouter(CUDY_HOST, CUDY_USERNAME, CUDY_PASSWORD, CUDY_PORT)

if not router.authenticate():
    print("Authentication error")
    exit()

sms_manager = get_sms_manager(router)

print("SMS Summary")
summary = sms_manager.get_sms_summary()
print(f"Inbox ...: {summary.inbox_count} with {summary.new_messages_count} new message(s)\nOutbox ..: {summary.outbox_count}")

print("\nSMS Inbox list")
inbox = sms_manager.get_sms_list("inbox")
for sms in inbox:
    print(f"{sms.index:2}: From: {sms.phone_number}, Received on: {sms.timestamp} (cfg:{sms.cfg})\n    Text: {sms.text}")

print("\nSMS Outbox list")
outbox = sms_manager.get_sms_list("outbox")
for sms in outbox:
    print(f"{sms.index:2}: To: {sms.phone_number}, Sent on: {sms.timestamp} (cfg:{sms.cfg})\n    Text: {sms.text}")

print("\nSMS")
sms = sms_manager.read_sms(outbox[0])
print(f"From: {sms.phone_number}\nText: {sms.text}")
