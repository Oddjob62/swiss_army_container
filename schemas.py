from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class CommandResult(BaseModel):
    command: str
    target: str
    output: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True

class Status(BaseModel):
    ip_address: str
    uptime: str