from fastapi import APIRouter
from .group import group_view
from .roles import role_view
from .users import user_view

auth_router = APIRouter()

auth_router.include_router(router=group_view.router, prefix="/groups", tags=["Groups"])
auth_router.include_router(
    router=role_view.router, prefix="/roles", tags=["Groups", "Users"]
)
auth_router.include_router(router=user_view.router, prefix="/users", tags=["Users"])
