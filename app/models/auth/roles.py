from app.models.base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Role(BaseModel):
    __tablename__ = "role"
    role = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    group_id = Column(Integer, ForeignKey('group.id'), nullable=True, default=None)
    #user = relationship("user",backref='children')