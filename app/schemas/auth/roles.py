from app.schemas.base import GetSchema, PostSchema, PatchSchema
from app.oauth.roles import RoleEnum
from pydantic import Field
from typing import List


class RolesPostSchema(PostSchema):
    role: RoleEnum
    user_id: int
    group_id: int = None


class RolesGetSchema(GetSchema, RolesPostSchema):
   ...
