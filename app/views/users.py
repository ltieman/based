from .base import BuildView
from fastapi_utils.cbv import cbv
from app.components import UserComponent

class UserView(BuildView):
    component = UserComponent
