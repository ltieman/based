from app.crud.base import BaseCrud
from app.models.roles import Role


class RoleCrud(BaseCrud):
    model = Role