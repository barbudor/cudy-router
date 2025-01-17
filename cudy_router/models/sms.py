from datetime import datetime
from pydantic import BaseModel


class SMSSummary(BaseModel):
    new_messages_count: int
    inbox_count: int
    outbox_count: int


class SMS(BaseModel):
    phone_number: str
    text: str
    index: int | None = None
    cfg: str | None = None
    timestamp: datetime | None = None
    box: str | None = None
