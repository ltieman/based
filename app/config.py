from pydantic import BaseSettings

class Config(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    REDIS_URL: str
    CLEAN_URL: str
