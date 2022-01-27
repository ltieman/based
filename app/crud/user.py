from .base import BaseCrud
from app.models import User
from app.config import Config
from sqlalchemy.orm import Session, Query
from typing import List, Union
import boto3
from app.schemas.user import UserGetSchema, UserCreatePostSchema,\
    UserLoginPostSchema, UserPatchSchema
from app.oauth import cognito_client

class BaseUserCrud(BaseCrud):
    model = User
if Config.COGNITO_REGION and Config.COGNITO_CLIENTID and Config.COGNITO_USERPOOLID:

    class CognitoUserCrud(BaseUserCrud):
        def post(cls,
                 session: Session,
                 data: UserCreatePostSchema) ->User:
            signup = cognito_client.sign_up(
                    ClientId=Config.COGNITO_CLIENTID,
                    Username=data.email,
                    Password=data.password,
                    UserAttributes=[
                        {"Name": "first_name","Value": data.first_name},
                        {"Name": "last_name", "Value": data.last_name},
                    ]
            )


        def get(cls,
                session: Session,
                id: int) ->User:
            pass

        def index(cls, session: Session,
                  params: dict= None,
                  for_head: bool = False) ->Union[List[User], Query]:
            pass

    class UserCrud(CognitoUserCrud):
        pass



elif Config.AUTH0_DOMAIN and Config.AUTH0_CLIENTID and Config.AUTH0_CUSTOMAPI:
    class Auth0UserCrud(BaseUserCrud):
        pass
    class UserCrud(Auth0UserCrud):
        pass