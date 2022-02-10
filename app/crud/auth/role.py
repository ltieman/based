from app.crud.base import BaseCrud
from app.models.role import Role


class RoleCrud(BaseCrud):
    model = Role