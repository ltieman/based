from fastapi.requests import Request
from app.schemas.user import UserWithRoles
from sqlalchemy.orm import Session
from app.models.base import BaseModel
from app.oauth.roles import RoleEnum
from app.crud.auth import AuthCrud
from app.config import config
from fastapi import Depends
from app.db import get_db
from typing import List
from fastapi.exceptions import HTTPException

class AuthCallable:
    required: bool = False
    override: bool = False

    def __init__(self, required: bool = False):
        self.required = required


    def __call__(self, request: Request,session: Session = Depends(get_db)):
        try:
            user = self.validate_code(session, request.cookies['AUTH-TOKEN'])
            self.additional_validation(user,request)
        except Exception as e:
            if self.required:
                raise HTTPException(401,"Not Authorized")
            else:
                user = None
        if self.override:
            try:
                return self.auth_logic(user), True
            except:
                return user, False
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
        session.close()
        return validated_user


class AuthRoleCheck(AuthCallable):
    def __init__(self, role: List[str], required: bool = False, model: BaseModel = None, override=False):
        self.required = required
        self.role = [r.name for r in role]
        self.override = override

    def auth_logic(self, user: dict):
        if RoleEnum.ADMIN.name in user.roles:
            return user
        if self.role:
            roles = set(user.roles).intersection(self.role)
            if not roles:
                raise HTTPException(401, "Not Authorized")
        return user


def AuthRoleOrSelfCheck(self, role: List[str], required: bool = False, model: BaseModel = None):
    auth_check = AuthRoleCheck(role=role, required=required, override=True)
    async def self_check(request: Request, session: Session = Depends(get_db)):
        user, role_check = auth_check(request=request, session=session)
        if role_check:
            return user
        try:
            if hasattr(model,'user_id'):
                if request.query_params.get('user_id', None):
                    assert request.query_params['user_id'] == user.id
                    return user
                data = await request.json()
                if data.get('user_id') == user.id:
                    return user
            elif model.__name__.lower() == 'user':
                if request.query_params.get('id', None):
                    assert request.query_params['id'] == user.id
                    return user
                data = await request.json()
                if data.get('id') == user.id:
                    return user
        except:
            pass
        raise HTTPException(401, "Not Authorized")
    return self_check



