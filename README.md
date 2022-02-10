# Based

Based is a luxury API framework built on top of FastAPI and FastAPI Utils.  Originally it was
intended to be a light API framework, but then I decided that I was lieing to myself when I said
that.  Based is an opinionated API framework that wants to give you all the tools you might want,
and then lets you pick which pieces you want to use.  The intention is to include everything from
authentication with Cognito and Auth0, static and dynamic RBAC, s3 file upload support, ELT with an Airbyte Connector,
kafka integration with Faust, and some other wild ideas.  And to do it the way I want to do it, in
a classful structure that I like hense, Based.

Other projects (like Piccolo) do similar things, but Based is designed to be extremely 
flexible (and use SQLAlchemy), and offer an expressive but light REST API framework that can
be built with very little code, or work as a base for whatever expansion I need 
(and use SQLAlchemy).

## Quick Start 
Below is an app I use in some of my tests.  All I am really doing is defining my interfaces,
in SQLAlchemy and Pydantic models, and composing those into the view.  This will create 
Post, Patch, Put, Get by ID, Get Index, Delete(Archive), UnDelete(UnArchive), and Head 
endpoints for the table I created.

```python
from app.models.base import BaseModel
from fastapi import FastAPI
from sqlalchemy import Column, String
from app.views.base import BaseBuildView
from app.schemas.base import GetSchema, PostSchema
from app.middleware import register_middleware
import uvicorn

#sqlalchemy database table
#inheirits id, created, modified, and archived columns
class TestsTable(BaseModel):
    name = Column(String)

#pydantic serialization models
#matches whats needed on the db model
#when using the matching verb
class TestPostSchema(PostSchema):
    name: str


class TestGetSchema(TestPostSchema, GetSchema):
    pass

#BuildBaseView Constructor Class builds our endpoints
class TestView(BaseBuildView):
    model = TestsTable
    get_schema = TestGetSchema
    post_schema = TestPostSchema
    patch_schema = TestPostSchema

#instantiate a FastAPI app
app = FastAPI()

#instantiate the Constructor and then give its constructed router to the FastAPI app
app.include_router(TestView().router, tags=['Test'])

#register the middleware which set up things like the database session
register_middleware(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

All of this is done with a constructor class that builds the View class as well as the Crud 
class, which lets me not have to do all that work every time. While FastAPI and FastAPI utils
have some peculiarities which seem to keep me from being able to have the API view class as
inheritable as I'd like, This Crud class is fully inheritable, and only requires 2 extra 
lines of code to declare explicitly.

This also makes it difficult to add additional methods to the router.  However, because its
all just FastAPI, you can specify an additional router, and the class will combine the two routers
at instantiation.

```python
from app.models.base import BaseModel
from fastapi import FastAPI, APIRouter
from sqlalchemy import Column, String
from app.crud.base import BaseCrud
from app.views.base import BaseBuildView
from app.schemas.base import GetSchema, PostSchema
from app.middleware import register_middleware
from sqlalchemy.orm import Session
import uvicorn


class TestsTable(BaseModel):
    name = Column(String)


class TestPostSchema(PostSchema):
    name: str


class TestGetSchema(TestPostSchema, GetSchema):
    pass

#this is an additional router to add a json_schema endpoint, assigned to the View Class
#as TestView.additional_router, and will here be available at /api/test/json-schema
additional_router = APIRouter()

@additional_router.get("/json-schema")
async def json_schema():
    return TestGetSchema.schema_json()
    

# this is the new CrudClass        
class TestCrud(BaseCrud):
    model = TestsTable

    def get(cls,
            session: Session,
            id: int) -> BaseModel:
        # I could do all sorts of things in here now
        return super().get(session=session, id=id)


# add the new crud class to the constructor instead of the SQLAlchemy Table
class TestView(BaseBuildView):
    # replace
    # model = TestTable
    # with
    crud_class = TestCrud
    additional_routes = additional_router
    get_schema = TestGetSchema
    post_schema = TestPostSchema
    patch_schema = TestPostSchema


app = FastAPI(root_path='/api')
app.include_router(TestView().router, tags=['Test'], prefix='/test')
register_middleware(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```





## ToDo:
* ~~Finish Endpoint Tests~~
* Document Existing Codebase with AutoGenerating Documentation
* Incorporate Coverage
* Streaming to Kafka
* Celery
* Auth
* Faust Subproject
* Admin Page Subproject
* RBAC