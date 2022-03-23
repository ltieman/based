from app.models.base import BaseModel
from fastapi import FastAPI
from datetime import datetime
from sqlalchemy import Column, String
from app.crud.base import BaseCrud
from app.views.base import BaseBuildView
from app.schemas.base import GetSchema, PostSchema
from app.middleware import register_middleware
from fastapi.testclient import TestClient
from app.db import get_fastapi_sessionmaker
from requests import Response
import pytest
import faker

index_count = 40
fake = faker.Faker()
session = get_fastapi_sessionmaker()


class UnitTestsTable2(BaseModel):
    name = Column(String)


BaseModel.metadata.create_all(session.cached_engine)

session = session.get_db().__next__()


class UnitTestBaseCrud(BaseCrud):
    model = UnitTestsTable2


class UnitTestPostSchema(PostSchema):
    name: str


class UnitTestGetSchema(UnitTestPostSchema, GetSchema):
    pass


class UnitTestPutSchema(UnitTestGetSchema):
    id: int = None
    created: datetime = None


class UnitTestView(BaseBuildView):
    model = UnitTestsTable2
    get_schema = UnitTestGetSchema
    post_schema = UnitTestPostSchema
    patch_schema = UnitTestPostSchema
    put_schema = UnitTestPutSchema


app = FastAPI()
app.include_router(UnitTestView().router)
register_middleware(app)
test_client = TestClient(app)


def create_data():
    return UnitTestPostSchema(name=fake.word())


@pytest.fixture
def post_data() -> UnitTestPostSchema:
    return create_data()


@pytest.fixture
def api_post(post_data: UnitTestPostSchema) -> Response:
    response = test_client.post("/", json=post_data.dict())
    return response


def test_api_post(post_data: UnitTestPostSchema, api_post: Response):
    assert api_post.status_code == 201
    jsonResponse = api_post.json()
    assert jsonResponse.get("name") == post_data.name


@pytest.fixture
def api_get(api_post: Response) -> Response:
    response = test_client.get(f"/{api_post.json().get('id')}")
    return response


def test_api_get(api_get: Response, api_post: Response):
    assert api_get.status_code == 200
    assert api_post.json() == api_get.json()


def test_patch(api_post: Response):
    update = create_data()
    response = test_client.patch(f"/{api_post.json().get('id')}", json=update.dict())
    assert response.status_code == 202
    assert response.json().get("id") == api_post.json().get("id")
    assert response.json().get("name") == update.name
    assert response.json().get("name") != api_post.json().get("name")


def test_update_put(api_post: Response):
    update = create_data()
    update_dict = update.dict()
    update_dict["id"] = api_post.json().get("id")
    response = test_client.put("/", json=update_dict)
    assert response.status_code == 202
    assert response.json().get("id") == api_post.json().get("id")
    assert response.json().get("name") == update.name
    new_put = create_data()
    new_put_response = test_client.put("/", json=new_put.dict())
    assert new_put_response.status_code == 202
    assert new_put_response.json().get("id") != response.json().get("id")
    assert new_put_response.json().get("name") == new_put.name


def test_UnitTestView_Auto_Component():
    view = UnitTestView()
    assert issubclass(view.crud_class, BaseCrud)
    assert view.crud_class.model == UnitTestsTable2


def test_clean_up_one():
    session.query(UnitTestsTable2).delete()
    session.commit()
    items = UnitTestBaseCrud.index(session=session)
    assert not items


@pytest.mark.parametrize("data", [create_data() for _ in range(index_count)])
def test_multi_api_post(data: UnitTestPostSchema) -> Response:
    response = test_client.post("/", json=data.dict())
    assert response.status_code == 201


def test_index():
    response = test_client.get("/")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 20
    for obj in json:
        by_id = test_client.get(f"/{obj['id']}")
        assert by_id.status_code == 200
        assert by_id.json() == obj
    response = test_client.get("/", params={"offset": 20})
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 20
    for obj in json:
        by_id = test_client.get(f"/{obj['id']}")
        assert by_id.status_code == 200
        assert by_id.json() == obj
    response = test_client.get("/", params={"offset": 40})
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 0


def test_head():
    response = test_client.head("/")
    assert response.status_code == 200
    assert int(response.headers["query-length"]) == 40


def test_archive_and_unarchive():
    index = test_client.get("/", params={"limit": 1})
    index_json = index.json()
    assert len(index_json) == 1
    response = test_client.delete(f"/{index_json[0]['id']}")
    assert response.status_code == 202
    assert response.json()["id"] == index_json[0]["id"]
    full_index = test_client.get("/", params={"limit": 40})
    assert len(full_index.json()) == 39
    head = test_client.head("/")
    assert int(head.headers["query-length"]) == 39
    full_index = test_client.get("/", params={"limit": 40, "show_archived": True})
    assert len(full_index.json()) == 40
    head = test_client.head("/", params={"limit": 40, "show_archived": True})
    assert int(head.headers["query-length"]) == 40
    response = test_client.delete(f"/undo/{index_json[0]['id']}")
    assert response.status_code == 202
    assert response.json()["id"] == index_json[0]["id"]
    full_index = test_client.get("/", params={"limit": 40})
    assert len(full_index.json()) == 40
    head = test_client.head("/")
    assert int(head.headers["query-length"]) == 40


def test_clean_up_two():
    session.query(UnitTestsTable2).delete()
    session.commit()
    items = UnitTestBaseCrud.index(session=session)
    assert not items
    # UnitTestsTable.__table__.drop(session)
