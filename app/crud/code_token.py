from base import BaseCrud
from app.models import Code_Token
from sqlalchemy.orm import Session, Query
from app.schemas.base import BaseModel
from app.schemas.code_token import CodeTokenSchema
from pydantic import BaseModel
from app.config import config
from cryptography.fernet import Fernet

fernet = Fernet(config.SECRET_KEY.encode())
if config.COGNITO_REGION:
    from app.oauth import cognito_client
    class CodeTokenCrud(BaseCrud):
        model = Code_Token

        @classmethod
        def post(cls,
                 session: Session,
                 data: BaseModel) ->BaseModel:
            data.token = fernet.encrypt(data.token)
            super().post(session,data)

        @classmethod
        def get(cls,
                session: Session,
                id: str,
                query: Query) ->CodeTokenSchema:
            item, *ignore = super().index(session=session, params={"code":id})
            token = fernet.decrypt(item.token.encode())
            item = CodeTokenSchema(token=token, code=item.code, user_id=item.user_id)
            return item

        @classmethod
        def validate_code(cls,
                          session: Session,
                          id: str):
            item = cls.get(session=session)
            user = cognito_client.get_user(AccessToken=item.token)


