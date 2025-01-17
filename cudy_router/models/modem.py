""" Modem Models"""

from typing import List
from pydantic import BaseModel


class NetworkAttributes(BaseModel):
    mcc: str
    mnc: str

class Network(BaseModel):
    name: str
    attributes: NetworkAttributes

class Cell(BaseModel):
    cell_id_hex: str
    cell_id: int
    enb: int
    sector: int
    pc_id: int

class ModemInfo(BaseModel):
    network: Network
    connected_time: int
    signal: int
    rssi: int
    rsrp: int
    rsrq: int
    sinr: int
    sim: int
    band: List[str]
    cell: Cell
