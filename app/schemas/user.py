from .base import GetSchema, PostSchema, PatchSchema

class UserGetSchema(GetSchema):
    token: str

class UserPostSchema(PostSchema):
    token: str

class UserPatchSchema(PatchSchema):
    token: str