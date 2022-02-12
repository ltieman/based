from app.crud.base import BaseCrud
from app.models import Code_Token
from sqlalchemy.orm import Session, Query
from app.schemas.auth.code_token import CodeTokenSchema
from pydantic import BaseModel
from app.config import config
from cryptography.fernet import Fernet
from app.schemas.user import UserWithRoles

fernet = Fernet(config.SECRET_KEY.encode())

if config.COGNITO_REGION:

    class CodeTokenCrud(BaseCrud):
        model = Code_Token

        @classmethod
        def post(
            cls, session: Session, data: BaseModel, user: UserWithRoles = None
        ) -> BaseModel:
            data.token = fernet.encrypt(data.token.encode())
            super().post(session, data, user=user)

        @classmethod
        def get(
            cls,
            session: Session,
            id: str,
            query: Query = None,
            user: UserWithRoles = None,
        ) -> CodeTokenSchema:
            try:
                query = session.query(cls.model).filter(cls.model.code == id)
                item = query.first()
                token = fernet.decrypt(item.token)
                item = CodeTokenSchema(
                    token=token, code=item.code, user_id=item.user_id
                )
                return item
            except:
                return None
