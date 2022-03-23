from app.models.base import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class Role(BaseModel):
    __tablename__ = "role"
    role = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("username.id"))
    group_id = Column(Integer, ForeignKey("group.id"), nullable=True, default=None)
    UniqueConstraint('role','group_id','user_id', name='role_group_unique')
    # username = relationship("username",backref='children')
