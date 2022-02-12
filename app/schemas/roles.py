from .base import GetSchema, PostSchema, PatchSchema
from pydantic import Field
from typing import List



class RolesPostSchema(PostSchema):
    role: str
    user_id: int


class RolesGetSchema(GetSchema, RolesPostSchema):
    pass

