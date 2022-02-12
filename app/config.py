from pydantic import BaseSettings
from cryptography.fernet import Fernet


class Config(BaseSettings):
    CLEAN_URL: str = "localhost"
    SECRET_KEY: str = Fernet.generate_key()
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    REDIS_URL: str = None
    API_PREFIX: str = "/v1"
    COGNITO_REGION: str = None
    COGNITO_USERPOOLID: str = None
    COGNITO_CLIENTID: str = None
    COGNITO_DOMAIN: str = None
    COGNITO_CLIENT_SECRET: str = None
    AUTH0_DOMAIN: str = None
    AUTH0_CUSTOMAPI: str = None
    AUTH0_CLIENTID: str = None


config = Config()
