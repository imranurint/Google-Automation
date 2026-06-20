# app/models/gmail_models.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class EmailSend(BaseModel):
    to: EmailStr
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = []
    bcc: Optional[List[EmailStr]] = []
    attachments: Optional[List[str]] = []

class EmailRead(BaseModel):
    id: str
    subject: str
    from_: str
    date: datetime
    snippet: str
    body: str

class EmailList(BaseModel):
    emails: List[EmailRead]
    total: int
    next_page_token: Optional[str] = None

