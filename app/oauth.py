from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from fastapi_cloudauth.auth0 import Auth0, Auth0CurrentUser, Auth0Claims
from .config import config
import boto3

#have no idea if this will work, but i think it will?
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


if config.COGNITO_REGION and config.COGNITO_CLIENTID and config.COGNITO_USERPOOLID:
    auth = Cognito(region=config.COGNITO_REGION,
                   userPoolId=config.COGNITO_USERPOOLID,
                   client_id=config.COGNITO_CLIENTID
                   )
    get_current_user = CognitoOptionalUser(
        region=config.COGNITO_REGION,
        userPoolId=config.COGNITO_USERPOOLID,
        client_id=config.COGNITO_CLIENTID
    )
    cognito_client = boto3.client('cognito-idp', region_name=config.COGNITO_REGION)

elif config.AUTH0_DOMAIN and config.AUTH0_CLIENTID and config.AUTH0_CUSTOMAPI:
    auth = Auth0(domain=config.AUTH0_DOMAIN,
                 customAPI=config.AUTH0_CUSTOMAPI)
    get_current_user = Auth0OptionalUser(
        domain=config.AUTH0_DOMAIN,
        client_id=config.COGNITO_CLIENTID
    )

