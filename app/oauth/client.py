from app.config import config
import boto3

if config.COGNITO_REGION:
    cognito_client = boto3.client("cognito-idp", region_name=config.COGNITO_REGION)

elif config.AUTH0_DOMAIN and config.AUTH0_CLIENTID and config.AUTH0_CUSTOMAPI:
    pass
