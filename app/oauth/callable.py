from fastapi.requests import Request
from app.schemas.auth.user import UserWithRoles, AnonymousUser
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

    def __init__(self, required: bool = False, model: BaseModel = None):
        self.required = required
        self.model = model


    def __call__(self, request: Request,session: Session = Depends(get_db)):
        try:
            try:
                user = self.validate_code(session, request.cookies['AUTH-TOKEN'])

            except:
                user = AnonymousUser()
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
        try:
            return self.auth_logic(user)
        except:
            raise HTTPException(401, "Not Authorized")

    def auth_logic(self, user: dict):
        #this is mostly here for overwriting and allowing us to do logic on user
        return user

    def additional_validation(self, user: UserWithRoles, request: Request):
        pass

    def validate_code(self,
                      session: Session,
                      code: str):
        try:
            validated_user = AuthCrud.validate_code(session=session,
                                                        code=code)
            validated_user.authorized_groups = [group_role.group_id for group_role in validated_user.group_roles if
                                      RoleEnum[group_role].value >= self.role.value]
        except:
            session.close()
            raise
        return validated_user


class AuthRoleCheck(AuthCallable):
    def __init__(self, role: RoleEnum, required: bool = False, model: BaseModel = None, override=False):
        self.required = required
        self.role = role
        self.override = override
        self.model = model

    def auth_logic(self, user: UserWithRoles):
        auth_status = False
        if RoleEnum.ADMIN.name in user.roles:
            auth_status = True
        if self.role:
            roles = [role for role in user.roles if RoleEnum[role].value >= self.role.value]
            if roles:
                auth_status = True
        if (hasattr(self.model, 'group_id') or self.model.__name__.lower() == 'group') and user.authorized_groups:
                auth_status = True
        if auth_status:
            return user
        else:
            raise HTTPException('401', 'Not Authorized')


def AuthRoleOrSelfCheck(self, role: List[str], required: bool = False, model: BaseModel = None):
    auth_check = AuthRoleCheck(role=role, required=required, override=True, model=model)
    async def self_check(request: Request, session: Session = Depends(get_db)):
        user, role_check = auth_check(request=request, session=session)
        session.close()
        if role_check:
            return user
        try:
            if hasattr(model,'user_id'):
                if request.query_params.get('user_id', None):
                    assert request.query_params['user_id'] == user.id
                    return user
                if request.path_params.get('user_id', None):
                    assert request.path_params.get('user_id') == user.id
                    return user
                data = await request.json()
                if data.get('user_id') == user.id:
                    return user
            elif model.__name__.lower() == 'user':
                if request.query_params.get('id', None):
                    assert request.query_params['id'] == user.id
                    return user
                if request.path_params.get('id', None):
                    assert request.path_params.get('id') == user.id
                    return user
                data = await request.json()
                if data.get('id') == user.id:
                    return user
        except:
            pass
        raise HTTPException(401, "Not Authorized")
    return self_check



