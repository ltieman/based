from app.schemas.base import GetSchema, PostSchema, PatchSchema

class GroupPostSchema(PostSchema):
    class Config:
        is_group_schema = True
    group: str

class GroupGetSchema(GroupPostSchema, GetSchema):
    pass