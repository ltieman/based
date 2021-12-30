from .base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime


class User(BaseModel):
    __tablename__ = "user"
    token = Column(String)

