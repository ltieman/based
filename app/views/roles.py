from app.models.roles import Role
from .base import BaseBuildView
from app.oauth.callable import AuthRoleOrSelfCheck
from app.oauth.roles import RoleEnum
from app.schemas.roles import RolesPostSchema, RolesGetSchema

class RoleView(BaseBuildView):
    model = Role
    auth_callable = AuthRoleOrSelfCheck
    require_auth = True
    required_role = [RoleEnum.ADMIN]
    get_schema = RolesGetSchema
    post_schema = RolesPostSchema
    available_routes = ['get','index','post','patch','put','delete','head','undelete']

role_view = RoleView()