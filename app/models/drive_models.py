# app/models/drive_models.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FileCreate(BaseModel):
    name: str
    mime_type: str = "application/octet-stream"
    parents: Optional[List[str]] = []

class FileInfo(BaseModel):
    id: str
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    web_view_link: Optional[str] = None

class FileList(BaseModel):
    files: List[FileInfo]
    next_page_token: Optional[str] = None

