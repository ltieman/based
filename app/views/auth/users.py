from app.views.base import BaseBuildView, view_base
from fastapi import Request, Response, Depends
from fastapi.responses import RedirectResponse
from app.crud.auth import AuthCrud
from app.oauth.callable import AuthRoleOrSelfCheck
from app.schemas.auth.user import UserGetSchema, UserCreatePostSchema, UserLoginPostSchema
from fastapi import APIRouter
from fastapi import exceptions
from app.config import config
from app.oauth.roles import RoleEnum
from sqlalchemy.orm import Session
from app.db import get_db
from app.views.enums import Routes
import secrets


additional_router = APIRouter()
if config.COGNITO_REGION:
    @additional_router.post("/login",response_model=UserGetSchema)
    def aws_cognito_auth_user_password(
            user_password: UserLoginPostSchema,
            response: Response,
            request: Request,
            session: Session = Depends(get_db)
    ):
        try:
            token = AuthCrud.user_login(user_password=user_password, request=request)
            code = secrets.token_urlsafe(32)
            user = AuthCrud.auth_callback(code=code, session=session, token=token,response=response,return_user=True)
            user = UserGetSchema.from_orm(user)
            session.close()
            return user
        except Exception as e:
            session.close()
            raise exceptions.HTTPException(401,'Not Authorized')

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

@view_base
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
    role_patch = RoleEnum.ADMIN
    available_routes = [
        Routes.get,
        Routes.index,
        Routes.delete,
        Routes.undelete,
        Routes.patch
    ]


