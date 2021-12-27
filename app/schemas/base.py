from pydantic import BaseModel
from datetime import datetime

class ArchiveUpdate(BaseModel):
    archive: datetime = datetime.now()

class PostSchema(BaseModel):
    pass

class GetSchema(BaseModel):
    created: datetime
    archive: datetime = None
    modified: datetime = None


class PatchSchema(BaseModel):
    pass

class Webargs(BaseModel):
    limit: int = 0
    offset: int = 0

class HeadSchema(Webargs):
    count: str