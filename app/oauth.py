from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from fastapi_cloudauth.auth0 import Auth0, Auth0CurrentUser, Auth0Claims
from .config import Config

class CognitoOptionalUser(CognitoCurrentUser):
    def __init__(self, *args,**kwargs):
        try:
            super().__init__(*args,**kwargs)
        except:
            self = None

class Auth0OptionalUser(Auth0CurrentUser):
    def __init__(self, *args,**kwargs):
        try:
            super().__init__(*args,**kwargs)
        except:
            self = None


if Config.COGNITO_REGION and Config.COGNITO_CLIENTID and Config.COGNITO_USERPOOLID:
    auth = Cognito(region=Config.COGNITO_REGION,
                   userPoolId=Config.COGNITO_USERPOOLID,
                   client_id=Config.COGNITO_CLIENTID
                   )
    get_current_user = CognitoOptionalUser(
        region=Config.COGNITO_REGION,
        userPoolId=Config.COGNITO_USERPOOLID,
        client_id=Config.COGNITO_CLIENTID
    )
elif Config.AUTH0_DOMAIN and Config.AUTH0_CLIENTID and Config.AUTH0_CUSTOMAPI:
    auth = Auth0(domain=Config.AUTH0_DOMAIN,
                 customAPI=Config.AUTH0_CUSTOMAPI)
    get_current_user = Auth0OptionalUser(
        domain=Config.AUTH0_DOMAIN,
        client_id=Config.COGNITO_CLIENTID
    )

