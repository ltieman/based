from app.crud.base import BaseCrud
from app.models import User
from app.config import config


class BaseUserCrud(BaseCrud):
    model = User


if config.COGNITO_REGION and config.COGNITO_CLIENTID and config.COGNITO_USERPOOLID:

    class CognitoUserCrud(BaseUserCrud):
        pass

    class UserCrud(CognitoUserCrud):
        pass

elif config.AUTH0_DOMAIN and config.AUTH0_CLIENTID and config.AUTH0_CUSTOMAPI:

    class Auth0UserCrud(BaseUserCrud):
        pass

    class UserCrud(Auth0UserCrud):
        pass

else:
    class UserCrud(BaseUserCrud):
        def __init__(self):
            raise Exception("Auth Has Not Been Configured")
