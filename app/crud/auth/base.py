from app.crud.base import BaseCrud
from app.crud.auth.user import UserCrud
from app.crud.auth.role import RoleCrud
from app.crud.auth.code_token import CodeTokenCrud, CodeTokenSchema
from app.schemas.user import UserWithRoles
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.config import config
from app.schemas.user import UserCreatePostSchema
from app.models import User, Code_Token
import requests

class AuthCrudBase(UserCrud):
    code_token_crud: CodeTokenCrud = CodeTokenCrud
    role_crud: RoleCrud = RoleCrud

    @classmethod
    def auth_callback(cls, *args, **kwargs):
        raise HTTPException(405, "Not Authorized")

    @classmethod
    def validate_code(cls, *args, **kwargs):
        raise HTTPException(405, "Not Authorized")



if config.COGNITO_REGION:
    from app.oauth.client import cognito_client
    class AWSAuthCrudBase(AuthCrudBase):
        @classmethod
        def get_user_from_aws_for_token(cls, token) -> UserCreatePostSchema:
            user = cognito_client.get_user(AccessToken=token)
            user_json = {attribute['Name']: attribute['Value'] for attribute in user.UserAttributes}
            user_json.update({"username": user['Username']})
            return UserCreatePostSchema(**user_json)

        @classmethod
        def auth_callback(cls,
                          code: str,
                          response: Response,
                          session: Session):
            token = requests.post(f"https://{config.COGNITO_DOMAIN}/oauth2/token",
                                  data={"grant_type": "authorization_code",
                                        "code": code,
                                        "client_id": config.COGNITO_CLIENTID,
                                        "redirect_uri": f"{config.CLEAN_URL}/users/login-callback"},
                                  auth=(config.COGNITO_CLIENTID, config.COGNITO_CLIENT_SECRET)
                                  )
            cookie = [cookie for cookie in token.cookies if cookie.name == 'XSRF-TOKEN'][0]
            response.set_cookie(key=cookie.name, value=cookie.value, path=cookie.path, expires=3600 * 48

                                )
            token_json = token.json()
            user_schema = cls.get_user_from_aws_for_token(token['access_token'])

            try:
                user, *ignore = cls.index(session=session,
                                          params={
                                              "sub": user_schema.sub
                                          })
            except:
                user = None
            if user:
                user = cls.update(session=session,
                                  id=user.id,
                                  data=user_schema
                                  )
            else:
                user = cls.post(session=session,
                                data=user_schema
                                )
            code_token = cls.code_token_crud.get(session=session,
                                           id=code
                                           )
            if not code_token:
                code_token = CodeTokenSchema(code=code, token=token_json['access_token'], user_id=user.id)
                cls.code_token_crud.post(session=session,
                                   data=code_token)

        @classmethod
        def validate_code(cls,
                          session: Session,
                          code: str):
            item = cls.code_token_crud.get(session=session,
                                           id = code)
            user_from_aws = cls.get_user_from_aws_for_token(item.token)
            user_from_db = cls.get(session=session,
                                   id=item.user_id)
            try:
                assert user_from_aws.sub == user_from_db.sub
            except:
                raise HTTPException(405,"Not Authorized")
            roles = cls.role_crud.index(session=session,
                                        params={"user_id":item.user_id})
            roles = list({
                role.role for role in roles
            })
            user_to_return = UserWithRoles.from_orm(user_from_db)
            user_to_return.roles = roles
            return user_to_return

    class AuthCrud(AWSAuthCrudBase):
        pass
else:
    class AuthCrud(AuthCrudBase):
        pass