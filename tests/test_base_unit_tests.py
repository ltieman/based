from app.models.base import Base
from sqlalchemy import Column, String
from app.components.base import CrudComponent
from app.schemas.base import GetSchema,PostSchema, Webargs
from app.db import  get_fastapi_sessionmaker
from fastapi.testclient import TestClient
from copy import deepcopy
import pytest
import faker

index_count = 40
fake = faker.Faker()
session = get_fastapi_sessionmaker()


class UnitTestsTable(Base):
    name = Column(String)

Base.metadata.create_all(session.cached_engine)

session = session.get_db().__next__()

class UnitTestCrudComponent(CrudComponent):
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
    return UnitTestCrudComponent.post(session=session, data=post_data)

def test_post(first_post):
    assert first_post.id
    assert first_post.name
    assert first_post.created
    assert not first_post.archived
    assert not first_post.updated

def test_get(first_post):
    item = UnitTestCrudComponent.get(session=session, id=first_post.id)
    assert item == first_post

def test_update(first_post, post_data):
    name = deepcopy(first_post.name)
    update_data = create_data()
    item = UnitTestCrudComponent.update(session=session, data= update_data, id=first_post.id)
    assert item.id == first_post.id
    assert item.name == update_data.name
    assert not item.name == name
    assert item.updated
    assert item.created == first_post.created

def test_archive(first_post):
    item = UnitTestCrudComponent.delete(session=session,
                                        id=first_post.id)
    assert item.archived
    assert item.id == first_post.id

def test_unarchived(first_post):
    item = UnitTestCrudComponent.delete(session=session,
                                        id=first_post.id)
    assert item.archived
    assert item.id == first_post.id
    unarchived = UnitTestCrudComponent.undelete(session=session,
                                                id= first_post.id)
    assert not unarchived.archived
    assert unarchived.id == first_post.id

def test_clean_up_one():
    session.query(UnitTestsTable).delete()
    session.commit()
    items = UnitTestCrudComponent.index(session=session)
    assert not items

@pytest.mark.parametrize('data', [create_data() for _ in range(index_count)])
def test_create_many(data):
    item = UnitTestCrudComponent.post(session=session, data=data)
    assert item

def test_head():
    head = UnitTestCrudComponent.head(session=session, params=Webargs())
    assert int(head.count) == index_count

def test_index():
    index = UnitTestCrudComponent.index(session=session, params=Webargs())
    assert len(index) == 20
    index = UnitTestCrudComponent.index(session=session, params=Webargs(offset=20))
    assert len(index) == 20
    index = UnitTestCrudComponent.index(session=session, params=Webargs(offset=40))
    assert not index




def test_clean_up():
    session.query(UnitTestsTable).delete()
    session.commit()
    items = UnitTestCrudComponent.index(session=session)
    assert not items

