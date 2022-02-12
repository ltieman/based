from .base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


class Group(BaseModel):
    __tablename__ = "group"
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
