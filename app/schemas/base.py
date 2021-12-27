from pydantic import BaseModel
from datetime import datetime
from typing import Union

class ArchiveUpdate(BaseModel):
    archived: Union[datetime, None] = datetime.now()

class PostSchema(BaseModel):
    pass

class GetSchema(BaseModel):
    created: datetime
    archived: datetime = None
    modified: datetime = None


class PatchSchema(BaseModel):
    pass

class Webargs(BaseModel):
    limit: int = 20
    offset: int = 1
    show_archived: bool = False

class HeadSchema(Webargs):
    count: str