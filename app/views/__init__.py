from fastapi import FastAPI
from .auth import auth_router


webapp = FastAPI(openapi_url="/api/openapi.json",route_path='/api')
webapp.include_router(auth_router)