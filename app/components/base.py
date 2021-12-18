from app.models.base import Base
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query
from typing import List, Union
from sqlalchemy import update
from app.schemas.base import ArchiveUpdate, HeadSchema

class CrudComponent:
    model: Base
    @classmethod
    def non_field_index_params(cls,
                               params: dict,
                               query: Query)->Query:
        return query

    @classmethod
    def get(cls,
            session: Session,
            id: int)->Base:
        return session.query(cls.model).filter(cls.model == id).first()

    @classmethod
    def index(cls, session: Session,
              params: BaseModel= None,
              for_head: bool = False)->Union[List[Base],Query]:
        if params:
            params = params.dict(exclude_unset=True)
        else:
            params = {}
        query = session.query(cls.model)
        for k,v in params.items():
            try:
                query = query.filter(getattr(cls.model,k) == v)
            except:
                pass
        query = cls.non_field_index_params(params=params,
                                           query=query)
        if for_head:
          return query
        return query.offset(params.get('offset',0)).limit(params.get('limit',20)).all()

    @classmethod
    def post(cls,
             session: Session,
             data: BaseModel)->Base:
        item = cls.model(**data.dict())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def update(cls,
               session,
               id: int,
               data: BaseModel)->Base:
        up_query = update(cls.model).where(cls.model == id).values(**data.dict())
        session.add(up_query)
        return cls.get(session,id)

    @classmethod
    def delete(cls,
               session: Session,
               id: int)->Base:
        return cls.update(session=session,id=id, data=ArchiveUpdate())

    @classmethod
    def head(cls,
             session: Session,
             params: BaseModel)->HeadSchema:
        query = cls.index(session=session,
                          params=params,
                          for_head=True)
        count = query.count()
        return HeadSchema(**params.dict(),count=count)

