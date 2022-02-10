from fastapi.requests import Request
from sqlalchemy.orm import Session
from app.crud.auth import AuthCrud
from app.config import config
from typing import List
from fastapi.exceptions import HTTPException

class AuthCallable:
    required: bool = False

    def __init__(self, required: bool = False):
        self.required = required


    def __call__(self, request: Request):
        try:
            user = self.validate_code(request.state.db, request.cookies['XSRF-TOKEN'])
        except Exception as e:
            if self.required:
                raise HTTPException("405","Not Authorized")
            else:
                user = None
        return self.auth_logic(user)

    def auth_logic(self, user: dict):
        #this is mostly here for overwriting and allowing us to do logic on user
        return user

    @classmethod
    def validate_code(cls,
                      session: Session,
                      code: str):
        validated_user = AuthCrud.validate_code(session=session,
                                                    code=code)
        return validated_user


class AuthRoleCheck(AuthCallable):
    def __init__(self, role: List[str], required: bool = False):
        self.required = required
        self.role = role

    def auth_logic(self, user: dict):
        if self.role:
            roles = set(user['role']).intersection(self.role)
            if not roles:
                raise HTTPException(405, "Not Authorized")
        return user