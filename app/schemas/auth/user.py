from app.schemas.base import GetSchema, PostSchema
from pydantic import Field, BaseModel
from typing import List
from app.oauth.roles import RoleEnum
from .roles import RolesGetSchema


class UserLoginPostSchema(PostSchema):
    email: str
    password: str


class UserCreatePostSchema(PostSchema):
    username: str
    sub: str
    email: str
    email_verified: bool
    first_name: str = Field(None, alias="given_name")
    last_name: str = Field(None, alias="family_name")

class UserUpdateSchema(PostSchema):
    email: str = None
    first_name: str = Field(None, alias="given_name")
    last_name: str = Field(None, alias="family_name")


class UserIndexSchema(GetSchema):
    username: str
    first_name: str
    last_name: str


class UserGetSchema(GetSchema):
    first_name: str
    last_name: str
    username: str
    sub: str
    email: str
    email_verified: bool


class UserWithRoles(UserGetSchema):
    roles: List[str] = []
    group_roles: List[RolesGetSchema] = []
    authorized_groups: List[int] = []


class AnonymousUser(BaseModel):
    roles: List[str] = [RoleEnum.OPEN.name]
    authorized_groups: List[int] = []
    group_roles: List[RolesGetSchema] = []

    def __bool__(self):
        ##this will override group security for endpoints marked for open use
        return False
