from fastapi import FastAPI
from .users import UserView
from app.config import config

webapp = FastAPI(openapi_url="/api/v1/openapi.json")
webapp.include_router(UserView().router,prefix=f"/users")
