# app/models/calendar_models.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EventDateTime(BaseModel):
    date_time: datetime
    time_zone: Optional[str] = "UTC"

class EventCreate(BaseModel):
    summary: str
    description: Optional[str] = None
    start: EventDateTime
    end: EventDateTime
    attendees: Optional[List[str]] = []

class EventInfo(BaseModel):
    id: str
    summary: str
    description: Optional[str]
    start: datetime
    end: datetime
    status: str
    html_link: str