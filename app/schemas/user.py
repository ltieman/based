from .base import GetSchema, PostSchema, PatchSchema
from pydantic import Field
from typing import List



class UserLoginPostSchema(PostSchema):
    email: str
    password: str

class UserCreatePostSchema(PostSchema):
    username: str
    sub: str
    email: str
    email_verified: bool
    first_name: str = Field(None, alias='given_name')
    last_name: str = Field(None, alias='family_name')

class UserGetSchema(GetSchema, UserCreatePostSchema):
    pass

class UserWithRoles(UserGetSchema):
    roles : List[str] = []

class UserPatchSchema(PatchSchema):
    token: str