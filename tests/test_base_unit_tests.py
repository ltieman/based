from app.models.base import TableBase
from sqlalchemy import Column, String
from app.components.base import CrudComponent
from app.schemas.base import GetSchema,PostSchema

class UnitTestsTable(TableBase):
    name = Column(String)

class UnitTestCrudComponent(CrudComponent):
    model = UnitTestsTable

class UnitTestPostSchema(PostSchema):
    name: str

class UnitTestGetSchema(UnitTestPostSchema, GetSchema):
    pass

