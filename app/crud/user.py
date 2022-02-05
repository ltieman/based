from .base import BaseCrud
from app.models import User
from app.config import config
from sqlalchemy.orm import Session, Query
from typing import List, Union
import boto3
from app.schemas.user import UserGetSchema, UserCreatePostSchema,\
    UserLoginPostSchema, UserPatchSchema
from app.oauth import cognito_client

class BaseUserCrud(BaseCrud):
    model = User
if config.COGNITO_REGION and config.COGNITO_CLIENTID and config.COGNITO_USERPOOLID:

    class CognitoUserCrud(BaseUserCrud):

        @classmethod
        def post(cls,
                 session: Session,
                 data: UserCreatePostSchema) ->User:
            signup = cognito_client.sign_up(
                    ClientId=config.COGNITO_CLIENTID,
                    Username=data.email,
                    Password=data.password,
                    UserAttributes=[
                        {"Name": "first_name","Value": data.first_name},
                        {"Name": "last_name", "Value": data.last_name},
                    ]
            )

        @classmethod
        def get(cls,
                session: Session,
                id: int) ->User:
            pass

        @classmethod
        def index(cls, session: Session,
                  params: dict= None,
                  for_head: bool = False) ->Union[List[User], Query]:
            pass

    class UserCrud(CognitoUserCrud):
        pass



elif config.AUTH0_DOMAIN and config.AUTH0_CLIENTID and config.AUTH0_CUSTOMAPI:
    class Auth0UserCrud(BaseUserCrud):
        pass
    class UserCrud(Auth0UserCrud):
        pass