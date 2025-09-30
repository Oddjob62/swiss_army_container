from sqlalchemy import Column, Integer, String, DateTime, Text, func, text
from datetime import datetime
from .database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CommandResult(Base):
    __tablename__ = "command_results"

    id = Column(Integer, primary_key=True, index=True)
    command = Column(String, nullable=False)
    target = Column(String, nullable=False)
    output = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("SYSDATETIMEOFFSET()"), nullable=False)