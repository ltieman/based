from app.models.base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Code_Token(BaseModel):
    __tablename__ = "code_token"
    token = Column(String, nullable=False)
    code = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("username.id"))
    # username = relationship("username",backref='children')
