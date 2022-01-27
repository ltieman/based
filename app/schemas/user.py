from .base import GetSchema, PostSchema, PatchSchema

class UserGetSchema(GetSchema):
    token: str

class UserLoginPostSchema(PostSchema):
    email: str
    password: str

class UserCreatePostSchema(UserLoginPostSchema):
    first_name: str
    last_name: str


class UserPatchSchema(PatchSchema):
    token: str