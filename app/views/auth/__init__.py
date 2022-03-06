from fastapi import APIRouter
from .group import GroupView as GroupView
from .roles import RoleView as RoleView
from .users import UserView as UserView

auth_router = APIRouter()

auth_router.include_router(router=GroupView.router, prefix="/groups", tags=["Groups"])
auth_router.include_router(
    router=RoleView.router, prefix="/roles", tags=["Groups", "Users"]
)
auth_router.include_router(router=UserView.router, prefix="/users", tags=["Users"])
