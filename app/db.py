from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, Session
from .config import config
from functools import lru_cache
from typing import Iterator
from fastapi_utils.session import FastAPISessionMaker

@lru_cache()
def get_fastapi_sessionmaker() -> FastAPISessionMaker:
    database_uri = config.SQLALCHEMY_DATABASE_URL
    return FastAPISessionMaker(database_uri)

def get_db() -> Iterator[Session]:
    """ FastAPI dependency that provides a sqlalchemy session """
    yield from get_fastapi_sessionmaker().get_db()