from .base import GetSchema, PostSchema, PatchSchema
from pydantic import Field

class UserGetSchema(GetSchema):
    token: str

class UserLoginPostSchema(PostSchema):
    email: str
    password: str

class UserCreatePostSchema(UserLoginPostSchema):
    username: str
    sub: str
    email: str
    email_verified: bool
    first_name: str = Field(None, alias='given_name')
    last_name: str = Field(None, alias='family_name')


class UserPatchSchema(PatchSchema):
    token: str