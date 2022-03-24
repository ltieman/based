from pydantic import BaseSettings
from cryptography.fernet import Fernet
from enum import Enum

class AppEnvironment(Enum):
    dev = 2
    test = 1
    prod = 3

class Config(BaseSettings):
    CLEAN_URL: str = "localhost"
    ##this is for development only, this will cause each agent, on each reboot, to have a different secret key
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
    APP_ENVIRONMENT: AppEnvironment = AppEnvironment.test


config = Config()
