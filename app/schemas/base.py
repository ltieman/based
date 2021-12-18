from pydantic import BaseModel
from datetime import datetime

class ArchiveUpdate(BaseModel):
    archive: datetime = datetime.now()

class PostSchema(BaseModel):
    pass

class GetSchema(BaseModel):
    pass

class PatchSchema(BaseModel):
    pass

class Webargs(BaseModel):
    limit: int = 0
    offset: int = 0

class HeadSchema(Webargs):
    count: str