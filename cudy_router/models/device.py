""" Modem Models"""

from typing import List, Optional
from pydantic import BaseModel



class Device(BaseModel):
    hostname: Optional[str] = None
    ip: str
    mac: str
    up_speed: float
    down_speed: float


class DevicesStats(BaseModel):
    top_downloader_speed: float
    top_downloader_mac: str
    top_downloader_hostname: str
    top_uploader_speed: float
    top_uploader_mac: str
    top_uploader_hostname: str
    total_down_speed: float
    total_up_speed: float


class DevicesInfo(BaseModel):
    device_count: int
    stats: DevicesStats
    devices: List[Device]
