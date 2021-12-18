from ..models.base import Base
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import update
from ..schemas.base import ArchiveUpdate

class CrudComponent:
    model: Base

    @classmethod
    def get(cls, session: Session, id: int)->Base:
        return session.query(cls.model).filter(cls.model == id).first()

    @classmethod
    def index(cls, session: Session, params: BaseModel= None)->List[Base]:
        if params:
            params = params.dict()
        else:
            params = {}
        query = session.query(cls.model)
        for k,v in params.items():
            try:
                query = query.filter(getattr(cls.model,k) == v)
            except:
                pass
        return query.offset(params.get('offset',0)).limit(params.get('limit',20)).all()

    @classmethod
    def post(cls, session: Session, data: BaseModel)->Base:
        item = cls.model(**data.dict())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def update(cls, session, id: int, data: BaseModel)->Base:
        up_query = update(cls.model).where(cls.model == id).values(**data.dict())
        session.add(up_query)
        return cls.get(session,id)

    @classmethod
    def delete(cls, session: Session, id: int)->Base:
        return cls.update(session=session,id=id, data=ArchiveUpdate())