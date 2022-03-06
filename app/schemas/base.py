from pydantic import BaseModel
from datetime import datetime
from typing import Union


class ArchiveUpdate(BaseModel):
    archived: Union[datetime, None] = datetime.now()


class PostSchema(BaseModel):
   ...


class GetSchema(BaseModel):
    class Config:
        orm_mode = True

    id: int
    created: datetime
    archived: datetime = None
    modified: datetime = None


class PatchSchema(BaseModel):
   ...


class HeadSchema(BaseModel):
    count: int
    limit: int = 20
    offset: int = 1
    show_archived: bool = False
