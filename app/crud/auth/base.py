from app.crud.auth.user import UserCrud
from app.crud.auth.role import RoleCrud
from app.oauth.roles import RoleEnum
from app.models.auth.user import User
from app.crud.auth.code_token import CodeTokenCrud
from app.schemas.auth.code_token import CodeTokenSchema
from app.schemas.auth.user import UserWithRoles, UserUpdateSchema, UserLoginPostSchema
from datetime import datetime
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.config import config
from app.schemas.auth.user import UserCreatePostSchema
from app.schemas.auth.roles import RolesPostSchema
from pydantic import BaseModel
from sqlalchemy.orm import Query
from app.models.base import BaseModel as SQLBaseModel
import requests
from typing import Union, List, Dict, Any
import hmac
import hashlib
import base64


class AuthCrudBase(UserCrud):
    code_token_crud: CodeTokenCrud = CodeTokenCrud
    role_crud: RoleCrud = RoleCrud

    @classmethod
    def query_params(
        cls,
        limit: int = 20,
        offset: int = 0,
        show_archived: bool = False,
        updated_since: datetime = None,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        username: str = None,
    ):
        return cls.__query_params__(**locals())

    @classmethod
    def auth_callback(cls, code: str,
                      response: Response,
                      session: Session,
                      token: str = None):
        if not token:
            token = cls.get_token_from_code(code)
            assert token.status_code == 200
            token_json = token.json()
        else:
            token_json = token
        response.set_cookie(
            key="AUTH-TOKEN",
            value=code,
            path="/",
            expires=3600 * 48
        )
        try:
            access_token = token_json["access_token"]
        except:
            access_token = token_json['AccessToken']
        user_dict = cls.get_user_for_token(access_token)
        user_schema = cls.user_format(user_dict)
        try:
            query = cls.index(
                session=session,
                params={
                    "sub": user_schema.sub,
                    'limit': 1},
                query_pass_back=True
            )
            user = query.first()
        except Exception as e:
            user = None
        if user:
            user = super().update(session=session,
                              id=user.id,
                              data=user_schema
                              )
        else:
            user = cls.post(session=session,
                            data=user_schema
                            )
            role_data = RolesPostSchema(user_id=user.id,
                                        role=RoleEnum.LOGIN.name)

            role = RoleCrud.post(session=session,
                                 data=role_data
                                 )
            assert role
        code_token = cls.code_token_crud.get(session=session,
                                             id=code
                                             )
        if not code_token:

            code_token = CodeTokenSchema(code=code,
                                         token=access_token,
                                         user_id=user.id
                                         )
            cls.code_token_crud.post(session=session,
                                     data=code_token
                                     )

    @classmethod
    def user_format(cls, user: dict) -> UserCreatePostSchema:
        user_json = {
            attribute["Name"]: attribute["Value"]
            for attribute in user["UserAttributes"]
        }
        user_json.update({"username": user["Username"]})
        return UserCreatePostSchema(**user_json)

    @classmethod
    def get_user_for_token(cls, token:str)->UserWithRoles:
        raise HTTPException(401,"Not Authorized")

    @classmethod
    def get_token_from_code(cls,code:str)->requests.Response:
        raise HTTPException(401,'Not Authorized')

    @classmethod
    def validate_code(cls, session: Session, code: str)->UserWithRoles:
        limit = 50
        offset = 0
        item = cls.code_token_crud.get(session=session, id=code)
        user_from_token = cls.get_user_for_token(item.token)
        user_from_token = cls.user_format(user_from_token)
        user_from_db = cls.get(session=session, id=item.user_id)
        try:
            assert user_from_token.sub == user_from_db.sub
        except:
            raise HTTPException(401, "Not Authorized")
        roles = []
        roles_pull = []
        while len(roles_pull) == limit or offset == 0:
            roles_pull = cls.role_crud.index(
                session=session,
                params={"user_id": item.user_id, "limit": limit, "offset": offset},
            )
            offset += limit
            roles += roles_pull

        top_roles = list({role.role for role in roles if role.group_id is None})
        group_roles = list({role for role in roles if role.group_id is not None})
        user_to_return = UserWithRoles.from_orm(user_from_db)
        user_to_return.roles = top_roles
        user_to_return.group_roles = group_roles
        return user_to_return

    @classmethod
    def update_remote_user(cls,
                           patch_user: User,
                           user_attributes: list
                               ):
        raise HTTPException(401, "Not Authorized")

    @classmethod
    def create_update_user_attributes(cls,
                                      data: UserUpdateSchema)->List[Dict[str,str]]:
        raise HTTPException(401, "Not Authorized")

    @classmethod
    def update(
        cls,
        session,
        id: int,
        data: UserUpdateSchema,
        query: Query = None,
        user: UserWithRoles = None,
        query_pass_back: bool = False
    ) -> Union[Query,SQLBaseModel]:
        user_attributes = cls.create_update_user_attributes(data=data)
        if user_attributes:
            if id == user.id:
                patch_user = user
            else:
                patch_user = cls.get(session, id)
            cls.update_remote_user(
                patch_user=patch_user,
                user_attributes=user_attributes
            )
            return super().update(session=session,
                         id=id,
                         data=data
                         )
        else:
            raise HTTPException(422, "No Data To Update User")


if config.COGNITO_REGION:
    from app.oauth.client import auth_client

    class AWSAuthCrudBase(AuthCrudBase):

        @classmethod
        def user_login(cls,
                       user_password: UserLoginPostSchema,
                       request: Request = None,
                       )->dict:
            key = bytes(config.COGNITO_CLIENT_SECRET,'latin-1')
            msg = bytes(user_password.username + config.COGNITO_CLIENTID, 'latin-1')
            new_digest = hmac.new(key,msg,hashlib.sha256).digest()
            secret_hash = base64.b64encode(new_digest).decode()
            if not request:
                authentication = auth_client.admin_initiate_auth(
                    UserPoolId = config.COGNITO_USERPOOLID,
                    ClientId = config.COGNITO_CLIENTID,
                    AuthFlow = 'ADMIN_USER_PASSWORD_AUTH',
                    AuthParameters = {
                        "SECRET_HASH": secret_hash,
                        "USERNAME": user_password.username,
                        "PASSWORD": user_password.password
                     })
            else:
                authentication = auth_client.admin_initiate_auth(
                    UserPoolId = config.COGNITO_USERPOOLID,
                    ClientId = config.COGNITO_CLIENTID,
                    AuthFlow = 'ADMIN_USER_PASSWORD_AUTH',
                    AuthParameters = {
                        "SECRET_HASH": secret_hash,
                        "USERNAME": user_password.username,
                        "PASSWORD": user_password.password
                     },

                    ContextData = {
                        'IpAddress': request.client.host,
                        'HttpHeaders':[
                            {
                                'headerName': header_key,
                                'headerValue': header_value
                            }
                            for header_key, header_value in request.headers.items()
                        ]
                        } )
            return authentication['AuthenticationResult']


        @classmethod
        def get_user_for_token(cls, token) -> dict:
            return auth_client.get_user(AccessToken=token)

        @classmethod
        def get_token_from_code(cls, code:str)->requests.Response:
            data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": config.COGNITO_CLIENTID,
                    "redirect_uri": f"{config.CLEAN_URL}/users/login-callback",
                }
            return requests.post(
                f"https://{config.COGNITO_DOMAIN}/oauth2/token",
                data=data,
                auth=(config.COGNITO_CLIENTID, config.COGNITO_CLIENT_SECRET),
            )

        @classmethod
        def create_update_user_attributes(cls,
                                          data: UserUpdateSchema
                                          )->List[Dict[str,str]]:
            user_attributes = []
            if data.email:
                user_attributes.append(
                    {
                        "Name": "Email",
                        "Value": data.email
                    }
                )
            if data.first_name:
                user_attributes.append(
                    {
                        "Name": "given_name",
                        "Value": data.first_name
                    }
                )
            if data.last_name:
                user_attributes.append(
                    {
                        "Name": "family_name",
                        "Value": data.last_name
                    }
                )
            return user_attributes

        @classmethod
        def update_remote_user(cls,
                               patch_user: User,
                               user_attributes: list
                               ):
                auth_client.admin_update_user_attributes(
                UserPoolId=config.COGNITO_USERPOOLID,
                Username=patch_user.username,
                UserAttributes=user_attributes)





    class AuthCrud(AWSAuthCrudBase):
        ...

else:

    class AuthCrud(AuthCrudBase):
        ...
