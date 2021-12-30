from fastapi import FastAPI
from .users import UserView
from app.config import config

webapp = FastAPI(openapi_url="/api/openapi.json",route_path='/api')
webapp.include_router(UserView().router,
                      prefix=f"/users",
                      tags=['Users']
                      )
