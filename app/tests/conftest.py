from pydantic import BaseSettings
import pytest
from app.db import get_fastapi_sessionmaker
from fastapi.testclient import TestClient


from app.main import webapp

@pytest.fixture
def test_client():
    return TestClient(webapp)

class UserLogin(BaseSettings):
    USER: str
    COGNITO_PASSWORD: str


@pytest.fixture
def user_login()-> UserLogin:
    return UserLogin()

@pytest.fixture
def sessionmaker():
    return get_fastapi_sessionmaker()

@pytest.fixture
def session(sessionmaker):
    return sessionmaker.get_db().__next__()