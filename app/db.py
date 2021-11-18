from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, Session
from .config import Config
from functools import lru_cache
from typing import Iterator
from fastapi_utils.session import FastAPISessionMaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# def get_db() -> Iterator[Session]:
#     """ FastAPI dependency that provides a sqlalchemy session """
#     yield from _get_fastapi_sessionmaker().get_db()


@lru_cache()
def get_fastapi_sessionmaker() -> FastAPISessionMaker:
    """ This function could be replaced with a global variable if preferred """
    database_uri = Config.SQLALCHEMY_DATABASE_URL
    return FastAPISessionMaker(database_uri)