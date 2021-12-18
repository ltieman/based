from .base import CrudComponent
from app.models import User

class UserComponent(CrudComponent):
    model = User