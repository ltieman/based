from app.views.base import BaseBuildView
from fastapi import Request, Response, Depends
from fastapi.responses import RedirectResponse
from app.crud.auth import AuthCrud
from app.oauth.callable import AuthRoleOrSelfCheck
from app.schemas.auth.user import UserGetSchema, UserCreatePostSchema
from fastapi import APIRouter
from fastapi import exceptions
from app.config import config
from app.oauth.roles import RoleEnum
from sqlalchemy.orm import Session
from app.db import get_db
from app.views.enums import Routes


additional_router = APIRouter()
if config.COGNITO_REGION:

    @additional_router.get("/login", response_class=RedirectResponse)
    async def aws_cognito_auth_flow_start():
        url = f"https://{config.COGNITO_DOMAIN}/login?response_type=code&client_id={config.COGNITO_CLIENTID}&redirect_uri={config.CLEAN_URL}/users/login-callback"
        return url

    @additional_router.get("/login-callback", response_class=RedirectResponse)
    def aws_cognito_get_token(
        code: str,
        response: Response,
        session: Session = Depends(get_db),
    ):
        try:
            AuthCrud.auth_callback(code=code, session=session, response=response)
            session.close()
        except Exception as e:
            session.close()
            raise exceptions.HTTPException(401, "Not Authorized")
        return f"{config.CLEAN_URL}/users/"


class UserView(BaseBuildView):
    crud_class = AuthCrud
    get_schema = UserGetSchema
    post_schema = UserCreatePostSchema
    additional_routes = additional_router
    require_auth = True
    auth_callable = AuthRoleOrSelfCheck
    role_delete = RoleEnum.ADMIN
    role_undelete = RoleEnum.ADMIN
    role_get = RoleEnum.ADMIN
    role_index = RoleEnum.LOGIN
    available_routes = [
        Routes.get,
        Routes.index,
        Routes.delete,
        Routes.undelete
    ]


user_view = UserView()
