from .base import BaseBuildView
from fastapi import Request
from fastapi.responses import RedirectResponse
from app.crud import UserCrud
from app.schemas.user import UserGetSchema, UserLoginPostSchema, UserPatchSchema, UserCreatePostSchema
from fastapi import APIRouter
from fastapi import exceptions
from app.config import config

additional_router = APIRouter()
if config.COGNITO_REGION:
    @additional_router.get("/login",response_class=RedirectResponse)
    def aws_cognito_auth_flow_start():
        url = f"https://{config.COGNITO_DOMAIN}/login?response_type=code&client_id={config.COGNITO_CLIENTID}&redirect_uri={config.CLEAN_URL}/users/login-callback"
        return url

    @additional_router.get("/login-callback",response_class=RedirectResponse)
    def aws_cognito_get_token(code:str,
                    request: Request):
        try:
            UserCrud.auth_callback(code=code, session=request.state.db)
            request.state.db.close()
        except:
            request.state.db.close()
            raise exceptions.HTTPException(405,"Not Authorized")
        return f"https://{config.CLEAN_URL}/home"

class UserView(BaseBuildView):
    crud_class = UserCrud
    get_schema = UserGetSchema
    post_schema = UserCreatePostSchema
    patch_schema = UserPatchSchema
    additional_routes = additional_router

user_view = UserView()


