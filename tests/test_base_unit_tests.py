from app.models.base import BaseModel
from sqlalchemy import Column, String
from app.crud.base import BaseCrud
from app.views.base import BaseBuildView
from app.schemas.base import GetSchema,PostSchema
from app.db import  get_fastapi_sessionmaker
from fastapi.testclient import TestClient
from copy import deepcopy
import pytest
import faker

index_count = 40
fake = faker.Faker()
session = get_fastapi_sessionmaker()


class UnitTestsTable(BaseModel):
    name = Column(String)






BaseModel.metadata.create_all(session.cached_engine)

session = session.get_db().__next__()

class UnitTestBaseCrud(BaseCrud):
    model = UnitTestsTable

class UnitTestPostSchema(PostSchema):
    name: str

class UnitTestGetSchema(UnitTestPostSchema, GetSchema):
    pass


def create_data():
    return UnitTestPostSchema(name=fake.word())

@pytest.fixture
def post_data()->UnitTestPostSchema:
    return create_data()

@pytest.fixture
def first_post(post_data)->UnitTestsTable:
    return UnitTestBaseCrud.post(session=session, data=post_data)

def test_post(first_post):
    assert first_post.id
    assert first_post.name
    assert first_post.created
    assert not first_post.archived
    assert not first_post.modified

def test_get(first_post):
    item = UnitTestBaseCrud.get(session=session, id=first_post.id)
    assert item == first_post

def test_update(first_post, post_data):
    name = deepcopy(first_post.name)
    update_data = create_data()
    item = UnitTestBaseCrud.update(session=session, data= update_data, id=first_post.id)
    assert item.id == first_post.id
    assert item.name == update_data.name
    assert not item.name == name
    assert item.modified
    assert item.created == first_post.created

def test_archive(first_post):
    item = UnitTestBaseCrud.delete(session=session,
                                   id=first_post.id)
    #assert item.archived
    assert item.id == first_post.id
    assert item.archived

def test_unarchived(first_post):
    item = UnitTestBaseCrud.delete(session=session,
                                   id=first_post.id)
    assert item.archived
    assert item.id == first_post.id
    unarchived = UnitTestBaseCrud.undelete(session=session,
                                           id= first_post.id)
    assert not unarchived.archived
    assert unarchived.id == first_post.id

def test_clean_up_one():
    session.query(UnitTestsTable).delete()
    session.commit()
    items = UnitTestBaseCrud.index(session=session)
    assert not items

@pytest.mark.parametrize('data', [create_data() for _ in range(index_count)])
def test_create_many(data):
    item = UnitTestBaseCrud.post(session=session, data=data)
    assert item

def test_head():
    head = UnitTestBaseCrud.head(session=session, params=UnitTestBaseCrud.query_params())
    assert int(head) == index_count

def test_index():
    index = UnitTestBaseCrud.index(session=session, params=UnitTestBaseCrud.query_params())
    assert len(index) == 20
    index = UnitTestBaseCrud.index(session=session, params=UnitTestBaseCrud.query_params(offset=20))
    assert len(index) == 20
    index = UnitTestBaseCrud.index(session=session, params=UnitTestBaseCrud.query_params(offset=40))
    assert not index

def test_clean_up_two():
    session.query(UnitTestsTable).delete()
    session.commit()
    items = UnitTestBaseCrud.index(session=session)
    assert not items


