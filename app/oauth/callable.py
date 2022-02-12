from fastapi.requests import Request
from app.schemas.user import UserWithRoles
from sqlalchemy.orm import Session
from app.oauth.roles import RoleEnum
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
            user = self.validate_code(request.state.db, request.cookies['AUTH-TOKEN'])
            self.additional_validation(user,request)
        except Exception as e:
            if self.required:
                raise HTTPException("405","Not Authorized")
            else:
                user = None
        return self.auth_logic(user)

    def auth_logic(self, user: dict):
        #this is mostly here for overwriting and allowing us to do logic on user
        return user

    def additional_validation(self, user: UserWithRoles, request: Request):
        pass

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
        self.role = [r.name for r in role]

    def auth_logic(self, user: dict):
        if RoleEnum.ADMIN.name in user.roles:
            return user
        if self.role:
            roles = set(user.roles).intersection(self.role)
            if not roles:
                raise HTTPException(405, "Not Authorized")
        return user

class AuthRoleOrSelfCheck(AuthRoleCheck):

    def additional_validation(self, user: UserWithRoles, request: Request):
        if request.query_params.get('user_id', None):
           assert request.query_params['user_id'] == user.id

