from fastapi import FastAPI
from .users import UserView

webapp = FastAPI(openapi_url="/api/openapi.json",route_path='/api')
webapp.include_router(UserView().router,
                      prefix="/users",
                      tags=['Users']
                      )
