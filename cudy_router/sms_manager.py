from typing import List

from . import CudyRouter
from . import cudy_parser
from .models.sms import SMSSummary, SMS

class SMSManager:

    def __init__(self, cudy_router: CudyRouter):
        self.cudy_router = cudy_router

    def get_sms_summary(self) -> SMSSummary:
        """ Retrieve SMS Summary """

        sms_summary = cudy_parser.get_sms_summary(self.cudy_router.get("admin/network/gcom/sms/status"))
        return SMSSummary.model_validate(sms_summary)

    def get_sms_list(self, box: str = "inbox") -> List[SMS]:
        """ Retrieve inbox or outbox list of messages """

        cudy_box = "rec" if box == "inbox" else "sto"
        sms_list = cudy_parser.get_sms_list(self.cudy_router.get(f"admin/network/gcom/sms/smslist?smsbox={cudy_box}"))
        for sms in sms_list:
            sms['box'] = box
        return [SMS.model_validate(sms) for sms in sms_list]

    def read_sms(self, cfg_or_sms: str | SMS, box: str = None) -> SMS:
        """ Read a SMS from one box """

        if isinstance(cfg_or_sms, SMS):
            cfg = cfg_or_sms.cfg
            box = cfg_or_sms.box if cfg_or_sms.box else box
        else:
            cfg = cfg_or_sms
        if box:
            cudy_box_arg = "&smsbox=rec" if box == "inbox" else "&smsbox=sto"
        else:
            cudy_box_arg = ""
        sms = cudy_parser.read_sms(self.cudy_router.get(f"admin/network/gcom/sms/readsms?cfg={cfg}{cudy_box_arg}"))
        if box:
            sms['box'] = box
        return SMS.model_validate(sms)

    def send_sms(self, phone_number: str, text: str):

        response = self.cudy_router.post("admin/network/gcom/sms/smsnew?nomodal=&iface=4g",
                                         body_multipart= {
                                             "cbi.submit": "1",
                                             "cbid.smsnew.1.phone": phone_number,
                                             "cbid.smsnew.1.content": text,
                                             "cbid.smsnew.1.send": "Send",
                                         })

        return response


def get_sms_manager(cudy_router: CudyRouter) -> SMSManager:
    return SMSManager(cudy_router)
