from app.crud.auth.group import GroupCrud
from app.views.base import BaseBuildView
from app.oauth.callable import AuthRoleOrSelfCheck
from app.oauth.roles import RoleEnum
from app.schemas.group import GroupPostSchema, GroupGetSchema


class GroupView(BaseBuildView):
    crud_class = GroupCrud
    auth_callable = AuthRoleOrSelfCheck
    require_auth = True
    required_role = RoleEnum.ADMIN
    role_post = RoleEnum.POST
    get_schema = GroupGetSchema
    post_schema = GroupPostSchema
    available_routes = [
        "get",
        "index",
        "post",
        "patch",
        "put",
        "delete",
        "head",
        "undelete",
    ]


group_view = GroupView()
