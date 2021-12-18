from pydantic import BaseSettings

class Config(BaseSettings):
    CLEAN_URL: str = None
    SECRET_KEY: str = None
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    REDIS_URL: str = None
    API_PREFIX: str = '/v1'

config = Config()