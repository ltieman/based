from .base import BaseCrud
from app.models import User

class UserCrud(BaseCrud):
    model = User