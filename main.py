from app.views import webapp
from app.middleware import register_middleware
import uvicorn

register_middleware(webapp)


if __name__ == "__main__":
    uvicorn.run(webapp, host="0.0.0.0", port=8000)