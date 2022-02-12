from app.crud.base import BaseCrud
from app.models.auth.roles import Role


class RoleCrud(BaseCrud):
    model = Role
