from pydantic import BaseSettings

class Config(BaseSettings):
    CLEAN_URL: str = None
    SECRET_KEY: str = None
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    REDIS_URL: str = None
    API_PREFIX: str = '/v1'
    COGNITO_REGION: str = None
    COGNITO_USERPOOLID: str = None
    COGNITO_CLIENTID: str = None
    AUTH0_DOMAIN: str = None
    AUTH0_CUSTOMAPI: str = None
    AUTH0_CLIENTID: str = None

config = Config()