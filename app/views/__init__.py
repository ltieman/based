from fastapi import FastAPI
from .users import user_view
from .roles import role_view

webapp = FastAPI(openapi_url="/api/openapi.json",route_path='/api')
webapp.include_router(user_view.router,
                      prefix="/users",
                      tags=['Users']
                      )
webapp.include_router(role_view.router,
                      prefix='/roles',
                      tags=['Users']
                      )
