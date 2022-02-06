from .base import BaseBuildView
from app.config import config
from fastapi import Request, Response
import requests
from fastapi_utils.cbv import cbv
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from app.crud import UserCrud
from app.crud.code_token import CodeTokenCrud
from app.schemas.user import UserGetSchema, UserLoginPostSchema, UserPatchSchema, UserCreatePostSchema
from app.schemas.code_token import CodeTokenSchema
from fastapi import APIRouter
from typing import Dict, List, Optional
from app.config import config

additional_router = APIRouter()
if config.COGNITO_REGION:
    from app.oauth import cognito_client
    @additional_router.post("/login/")
    def login(data: UserLoginPostSchema) -> UserGetSchema:
        item = user_view.crud_class.login(data)
        item = UserGetSchema.from_orm(item)
        return item

    @additional_router.get("/login",response_class=RedirectResponse)
    def aws_cognito_auth_flow_start():
        url = f"https://{config.COGNITO_DOMAIN}/login?response_type=code&client_id={config.COGNITO_CLIENTID}&redirect_uri={config.CLEAN_URL}/users/login-callback"
        return url

    @additional_router.get("/login-callback",response_model=RedirectResponse)
    def aws_cognito_get_token(code:str,
                    request: Request):
        token = requests.post(f"https://{config.COGNITO_DOMAIN}/oauth2/token",
                              data={"grant_type":"authorization_code",
                                    "code":code,
                                    "client_id": config.COGNITO_CLIENTID,
                                    "redirect_uri": f"{config.CLEAN_URL}/users/check"},
                              auth=(config.COGNITO_CLIENTID,config.COGNITO_CLIENT_SECRET)
                      )
        token_json = token.json()
        user = cognito_client.get_user(AccessToken=token_json['access_token'])
        user_json = {attribute['Name']: attribute['Value'] for attribute in user.UserAttributes}
        user_json.update({"username":user['Username']})
        user_schema = UserCreatePostSchema(**user_json)
        user, *ignore = UserCrud.index(session=request.state.db,
                              params={
                                  "sub":user_schema.sub
                              })
        if user:
            user = UserCrud.update(session=request.state.db,
                                   id=user.id,
                                   data=user_schema
                                   )
        else:
            user = UserCrud.post(session=request.state.db,
                                 data=user_schema
                                 )
        code_token = CodeTokenCrud.get(session=request.state.db,
                                       id=code
                                       )
        if not code_token:
            code_token = CodeTokenSchema(code=code, token=token_json['access_token'], user_id=user.id)
            code_token = CodeTokenCrud.post(session=request.state.db,
                                            data=code_token)
        return f"https://{config.CLEAN_URL}/home"

class UserView(BaseBuildView):
    crud_class = UserCrud
    get_schema = UserGetSchema
    post_schema = UserCreatePostSchema
    patch_schema = UserPatchSchema
    additional_routes = additional_router

user_view = UserView()


