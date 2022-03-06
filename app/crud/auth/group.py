from app.crud.base import BaseCrud
from app.models import Group
from sqlalchemy.orm import Session
from app.oauth.roles import RoleEnum
from app.schemas.auth.group import GroupPostSchema
from app.schemas.auth.user import UserWithRoles
from app.schemas.auth.roles import RolesPostSchema
from app.models.base import BaseModel as SQLBaseModel
from .role import RoleCrud


class GroupCrud(BaseCrud):
    model = Group

    def post(
        cls, session: Session, data: GroupPostSchema, user: UserWithRoles = None
    ) -> SQLBaseModel:
        item = super.post(session=session, data=data, user=user)
        role = RolesPostSchema(
            user_id=user.id, group_id=item.id, role=RoleEnum.ADMIN.name
        )
        RoleCrud.post(session=session, data=role, user=user)
        return item
