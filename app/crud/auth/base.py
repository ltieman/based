from app.crud.auth.user import UserCrud
from app.crud.auth.role import RoleCrud
from app.oauth.roles import RoleEnum
from app.crud.auth.code_token import CodeTokenCrud, CodeTokenSchema
from app.schemas.user import UserWithRoles
from datetime import datetime
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.config import config
from app.schemas.user import UserCreatePostSchema
from app.schemas.auth.roles import RolesPostSchema
import requests


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
    def auth_callback(cls, *args, **kwargs):
        raise HTTPException(401, "Not Authorized")

    @classmethod
    def validate_code(cls, *args, **kwargs):
        raise HTTPException(401, "Not Authorized")


if config.COGNITO_REGION:
    from app.oauth.client import cognito_client

    class AWSAuthCrudBase(AuthCrudBase):
        @classmethod
        def get_user_from_aws_for_token(cls, token) -> UserCreatePostSchema:
            user = cognito_client.get_user(AccessToken=token)
            user_json = {
                attribute["Name"]: attribute["Value"]
                for attribute in user["UserAttributes"]
            }
            user_json.update({"username": user["Username"]})
            return UserCreatePostSchema(**user_json)

        @classmethod
        def auth_callback(cls, code: str, response: Response, session: Session):
            token = requests.post(
                f"https://{config.COGNITO_DOMAIN}/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": config.COGNITO_CLIENTID,
                    "redirect_uri": f"{config.CLEAN_URL}/users/login-callback",
                },
                auth=(config.COGNITO_CLIENTID, config.COGNITO_CLIENT_SECRET),
            )
            # cookie = [cookie for cookie in token.cookies if cookie.name == 'XSRF-TOKEN'][0]
            assert token.status_code == 200
            response.set_cookie(
                key="AUTH-TOKEN", value=code, path="/", expires=3600 * 48
            )
            token_json = token.json()
            user_schema = cls.get_user_from_aws_for_token(token_json["access_token"])

            try:
                user, *ignore = cls.index(
                    session=session, params={"sub": user_schema.sub}
                )
            except:
                user = None
            if user:
                user = cls.update(session=session, id=user.id, data=user_schema)
            else:
                user = cls.post(session=session, data=user_schema)
                role_data = RolesPostSchema(user_id=user.id, role=RoleEnum.LOGIN.name)
                role = RoleCrud.post(session=session, data=role_data)
            code_token = cls.code_token_crud.get(session=session, id=code)
            if not code_token:
                code_token = CodeTokenSchema(
                    code=code, token=token_json["access_token"], user_id=user.id
                )
                cls.code_token_crud.post(session=session, data=code_token)

        @classmethod
        def validate_code(cls, session: Session, code: str):
            limit = 50
            offset = 0
            item = cls.code_token_crud.get(session=session, id=code)
            user_from_aws = cls.get_user_from_aws_for_token(item.token)
            user_from_db = cls.get(session=session, id=item.user_id)
            try:
                assert user_from_aws.sub == user_from_db.sub
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

    class AuthCrud(AWSAuthCrudBase):
        pass

else:

    class AuthCrud(AuthCrudBase):
        pass
