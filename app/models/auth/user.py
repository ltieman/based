from app.models.base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


class User(BaseModel):
    __tablename__ = "user"
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    email_verified = Column(Boolean, nullable=True)
    sub = Column(String,nullable=False)

