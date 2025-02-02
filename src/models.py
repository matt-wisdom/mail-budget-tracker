from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EmailData(BaseModel):
    id: str
    subject: str
    sender: str
    date_received: datetime
    body: str


class Transaction(BaseModel):
    amount: float
    currency: str
    date: datetime
    bank_name: str
    sender: Optional[str] = None
    receiver: Optional[str] = None
    transaction_type: str  # e.g., deposit, withdrawal, transfer, etc.
    classification: str  # e.g., personal, business, salary, etc.
    account_number: Optional[str] = None
    transaction_id: Optional[str] = None
    description: Optional[str] = None
