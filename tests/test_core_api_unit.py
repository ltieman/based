from app.models.base import BaseModel
from fastapi import FastAPI
from sqlalchemy import Column, String
from app.crud.base import BaseCrud
from app.views.base import BaseBuildView
from app.schemas.base import GetSchema, PostSchema
from app.middleware import register_middleware
from fastapi.testclient import TestClient
from requests import Response
import pytest
import faker

fake = faker.Faker()


class UnitTestsTable(BaseModel):
    name = Column(String)

class UnitTestBaseCrud(BaseCrud):
    model = UnitTestsTable

class UnitTestPostSchema(PostSchema):
    name: str

class UnitTestGetSchema(UnitTestPostSchema, GetSchema):
    class Config:
        orm_mode = True

class UnitTestView(BaseBuildView):
    model = UnitTestsTable
    get_schema = UnitTestGetSchema
    post_schema = UnitTestPostSchema
    patch_schema = UnitTestPostSchema

app = FastAPI()
app.include_router(UnitTestView().router)
register_middleware(app)
test_client = TestClient(app)

def create_data():
    return UnitTestPostSchema(name=fake.word())

@pytest.fixture
def post_data()->UnitTestPostSchema:
    return create_data()

@pytest.fixture
def api_post(post_data: UnitTestPostSchema)->Response:
    response = test_client.post('/', json=post_data.dict())
    return response


def test_api_post(post_data: UnitTestPostSchema, api_post:Response):
    assert api_post.status_code == 201
    jsonResponse = api_post.json()
    assert jsonResponse.get('name') == post_data.name

@pytest.fixture
def api_get(api_post:Response)->Response:
    response = test_client.get(f"/{api_post.json().get('id')}")
    return response

def test_api_get(api_get:Response, api_post:Response):
    assert api_get.status_code == 200
    assert api_post.json() == api_get.json()


def test_UnitTestView_Auto_Component():
    view = UnitTestView()
    assert issubclass(view.component, BaseCrud)
    assert view.component.model == UnitTestsTable
