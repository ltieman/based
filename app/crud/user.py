from .base import BaseCrud
from app.models import User
from app.config import config
from sqlalchemy.orm import Session, Query
import requests
from .code_token import CodeTokenCrud
from app.schemas.code_token import CodeTokenSchema
from typing import List, Union
from app.schemas.user import UserGetSchema, UserCreatePostSchema,\
    UserLoginPostSchema, UserPatchSchema

class BaseUserCrud(BaseCrud):
    model = User
if config.COGNITO_REGION and config.COGNITO_CLIENTID and config.COGNITO_USERPOOLID:
    from app.oauth import cognito_client


    class CognitoUserCrud(BaseUserCrud):

        @classmethod
        def auth_callback(cls,
                          code: str,
                          session: Session):
            token = requests.post(f"https://{config.COGNITO_DOMAIN}/oauth2/token",
                                  data={"grant_type": "authorization_code",
                                        "code": code,
                                        "client_id": config.COGNITO_CLIENTID,
                                        "redirect_uri": f"{config.CLEAN_URL}/users/check"},
                                  auth=(config.COGNITO_CLIENTID, config.COGNITO_CLIENT_SECRET)
                                  )
            token_json = token.json()
            user = cognito_client.get_user(AccessToken=token_json['access_token'])
            user_json = {attribute['Name']: attribute['Value'] for attribute in user.UserAttributes}
            user_json.update({"username": user['Username']})
            user_schema = UserCreatePostSchema(**user_json)
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
            code_token = CodeTokenCrud.get(session=session,
                                           id=code
                                           )
            if not code_token:
                code_token = CodeTokenSchema(code=code, token=token_json['access_token'], user_id=user.id)
                CodeTokenCrud.post(session=session,
                                    data=code_token)


    class UserCrud(CognitoUserCrud):
        pass



elif config.AUTH0_DOMAIN and config.AUTH0_CLIENTID and config.AUTH0_CUSTOMAPI:
    class Auth0UserCrud(BaseUserCrud):
        pass
    class UserCrud(Auth0UserCrud):
        pass