from datetime import datetime
from pydantic import BaseModel


class EmailData(BaseModel):
    subject: str
    sender: str
    date_received: datetime
    body: str
