from .base import BaseBuildView
from fastapi_utils.cbv import cbv
from app.crud import UserCrud
from app.schemas.user import UserGetSchema, UserPostSchema, UserPatchSchema

class UserView(BaseBuildView):
    crud_class = UserCrud
    get_schema = UserGetSchema
    post_schema = UserPostSchema
    patch_schema = UserPatchSchema
