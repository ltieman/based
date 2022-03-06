from app.crud.auth.group import GroupCrud
from app.views.base import BaseBuildView, view_base
from app.oauth.callable import AuthRoleOrSelfCheck
from app.oauth.roles import RoleEnum
from app.schemas.auth.group import GroupPostSchema, GroupGetSchema

@view_base
class GroupView(BaseBuildView):
    crud_class = GroupCrud
    auth_callable = AuthRoleOrSelfCheck
    require_auth = True
    required_role = RoleEnum.ADMIN
    role_post = RoleEnum.POST
    get_schema = GroupGetSchema
    post_schema = GroupPostSchema



