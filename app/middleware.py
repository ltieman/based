from fastapi import Request
from .db import get_fastapi_sessionmaker

def register_middleware(app):
    @app.middleware("http")
    async def add_db_sessions(request: Request, call_next):
        request.state.db = get_fastapi_sessionmaker().get_db().__next__()
        response = await call_next(request)
        #request.state.db.close()
        return response