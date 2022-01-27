from app.models.base import BaseModel
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session, Query
from typing import List, Union, Any
from sqlalchemy import update
from app.schemas.base import ArchiveUpdate, HeadSchema
from dateutil.parser import parse

class BaseCrud:
    model: BaseModel

    @classmethod
    def index_params(cls,
                    params: dict,
                    query: Query)->Query:
        try:
            #if show archived is set to false, return only rows where archived is none
            if not params['show_archived']:
                query = query.filter(cls.model.archived == None)
            #del params['show_archived']
        except:
            pass
        try:
            if params['updated_since']:
                #set query to return only rows created or updated since the date in the params
                query = query.filter(cls.model.created >=params['updated_since']| cls.model.updated >= params['updated_since'])
        except:
            pass
        #for every query param that matches up with a field name, return rows with the value
        for k,v in params.items():
            if hasattr(cls.model,k) and k not in ['offset', 'limit', 'show_archived', 'updated_since']:
                query = query.filter(getattr(cls.model,k) == v)
        return query

    @classmethod
    def get(cls,
            session: Session,
            id: int)->BaseModel:
        #simple get by id
        item = session.query(cls.model).filter(cls.model.id == id).first()
        return item

    @classmethod
    def index(cls, session: Session,
              params: dict= None,
              for_head: bool = False)->Union[List[BaseModel], Query]:
        if not params:
            params = {}
        query = session.query(cls.model)
        #this modifies the query based on the query params
        query = cls.index_params(params=params,
                                 query=query)

        #returns the query without executing it for the head method
        if for_head:
            return query
        #sets the offset and limit from the params and fetches the query
        return query.offset(params.get('offset',0)).limit(params.get('limit',20)).all()

    @classmethod
    def post(cls,
             session: Session,
             data: BaseModel)->BaseModel:

        #very straight forward sql alchemy create row
        item = cls.model(**data.dict())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def update(cls,
               session,
               id: int,
               data: BaseModel)->BaseModel:

        #again, standard SQL Alchemy update statment
        up_query = update(cls.model).where(cls.model.id == id).values(**data.dict(exclude_unset=True))
        session.execute(up_query)
        session.commit()
        return cls.get(session,id)

    @classmethod
    def delete(cls,
               session: Session,
               id: int)->BaseModel:
        #uses the update method to modify the archived field
        return cls.update(session=session,id=id, data=ArchiveUpdate(archived = datetime.utcnow()))

    @classmethod
    def undelete(cls,
               session: Session,
               id: int) -> BaseModel:
        #uses the update field to nullify the archived field
        return cls.update(session=session, id=id, data=ArchiveUpdate(archived=None))

    @classmethod
    def head(cls,
             session: Session,
             params: BaseModel)->HeadSchema:
        #get back the exact query that we would get from the index method
        query = cls.index(session=session,
                          params=params,
                          for_head=True)
        #get the count of the rows on the dataset
        return query.count()
        #give it back along with the params we were given


    @staticmethod
    def query_params(limit: int = 20, offset: int = 0, show_archived: bool = False, updated_since: datetime = None):
        #this code takes the parameters specified above for use as query parameters and returns them as a dictionary
        #as well as doing a little bit of parsing
        return BaseCrud.__query_params__(**locals())

    @staticmethod
    def __query_params__(**kwargs):
        if kwargs["updated_since"]:
            kwargs['updated_since'] = parse(kwargs["updated_since"])
        return {k: v for k, v in kwargs.items() if v is not None}