from typing import List
import fastapi
from fastapi import Request
from starlette.responses import RedirectResponse
from datetime import datetime
from pydantic import BaseModel
from secrets import token_urlsafe
from sqlalchemy import create_engine, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime)
    archived = Column(DateTime)

class Session(Base):
    __tablename__ = "session"
    user_id=Column(Integer, ForeignKey('user.id'))
    session = Column(String, default=token_urlsafe(32))
    created = Column(DateTime, default=datetime.now())


class Shortener(Base):
    __tablename__ = "shorterner"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=False, index=True)
    shortened = Column(String, index=True, unique=True, default=token_urlsafe(8))
    user_id = Column(Integer,ForeignKey('user.id'))
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime)
    archived = Column(DateTime)

class Vistors(Base):
    __tablename__ = 'visitors'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey('user.id'))
    shortener_id = Column(Integer, ForeignKey("shortener.id"))
    ip = Column(String)
    visited = Column(DateTime, default=datetime.now())

Base.metadata.create_all(bind=engine)

class ArchiveUpdate(BaseModel):
    archive: DateTime = datetime.now()

class ShortenPost(BaseModel):
    url: str
    shortened: str = None

class ShortenGet(ShortenPost):
    class Config:
        orm_mode = True
    id: int
    token: str
    created: DateTime
    updated: DateTime = None
    archived: DateTime = None

class VisitorsGet(BaseModel):
    shortener_id: int
    ip: str
    visited: DateTime

class Webargs(BaseModel):
    limit: int = 0
    offset: int = 0

class CrudComponent:
    model: Base
    post_schema: BaseModel = None
    get_schema: BaseModel = None

    @classmethod
    def get(cls, session: Session, id: int)->Base:
        return session(cls.model).filter(cls.model == id).first()

    @classmethod
    def index(cls, session: Session, params: BaseModel)->List[Base]:
        params = params.dict()
        query = session(cls.model)
        for k,v in params.items():
            try:
                query = query.filter(getattr(cls.model,k) == v)
            except:
                pass
        return query.offset(params['offset']).limit(params['limit']).all()

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

class ShortenComponent(CrudComponent):
    model = Shortener
    post_schema = ShortenPost
    get_schema = ShortenGet

    @classmethod
    def update(cls, session, id: int, token:str, data: ShortenPost)->Shortener:
        up_query = update(cls.model).where(cls.model == id).where(cls.model.token==token).values(**data.dict())
        session.add(up_query)
        return cls.get(session,id)

    @classmethod
    def delete(cls, session: Session, id: int, token: str)->Shortener:
        return cls.update(session=session,id=id, data=ArchiveUpdate(), token=token)

class VisitorComponent(CrudComponent):
    model = Vistors
    post_schema = VisitorsGet
    get_schema = VisitorsGet

class SessionComponent(CrudComponent):
    model = Session

    @classmethod
    def get(cls, session: Session, token: str)->Base:
        return session(cls.model).filter(cls.model.token == token).first()

class UserComponent(CrudComponent):
    model = User



app = fastapi.FastAPI()




@app.get("/{id}")
def redirect_url(id:int, request: Request):
    item = ShortenComponent.get(session=request.state.db, id=id)
    return RedirectResponse(url=item.url)

@app.post("/")
def post():
    pass

@app.patch("/{id}/{token}")
def patch():
    pass

@app.delete("/{id}/{token}")

@app.get("/{id:str}/{token}/visitors")
def get_visitors():
    pass

@app.get("/{id}/{token}/visitors/")
def get_visitor_stats():
    pass
