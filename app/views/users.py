from .base import BaseBuildView
from app.config import config
from fastapi_utils.cbv import cbv
from fastapi.responses import RedirectResponse
from app.crud import UserCrud
from app.schemas.user import UserGetSchema, UserLoginPostSchema, UserPatchSchema, UserCreatePostSchema
from fastapi import APIRouter

additional_router = APIRouter()

@additional_router.post("/login/")
def login(data: UserLoginPostSchema) -> UserGetSchema:
    item = user_view.crud_class.login(data)
    item = UserGetSchema.from_orm(item)
    return item

@additional_router.get("/login",response_class=RedirectResponse)
def login_redirect():
    url = f"https://{config.COGNITO_DOMAIN}/login?response_type=token&client_id={config.COGNITO_CLIENTID}&redirect_uri={config.CLEAN_URL}/oauth2/idpresponse"
    return url

@additional_router.get("/oauth2/idpresponse")
def login_idpresponse():
    pass

class UserView(BaseBuildView):
    crud_class = UserCrud
    get_schema = UserGetSchema
    post_schema = UserCreatePostSchema
    patch_schema = UserPatchSchema
    additional_routes = additional_router

user_view = UserView()


